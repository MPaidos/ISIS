from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Order, ChecklistItem, PhotoReport, Part
from .forms import PartForm


@login_required
def mechanic_dashboard(request):
    """Дашборд механика: свободные заказы и мои заказы"""
    if request.user.role not in ['mechanic', 'owner', 'admin']:
        messages.error(request, 'Доступ запрещён')
        return redirect('home')

    # Заказы, назначенные на этого механика
    my_orders = Order.objects.filter(
        mechanic=request.user,
        status__in=['new', 'in_progress']
    ).select_related('appointment')

    # Свободные заказы (без механика)
    available_orders = Order.objects.filter(
        mechanic__isnull=True,
        status='new'
    ).select_related('appointment')

    # Завершённые заказы
    completed_orders = Order.objects.filter(
        mechanic=request.user,
        status='completed'
    ).select_related('appointment')[:5]

    return render(request, 'orders/dashboard.html', {
        'my_orders': my_orders,
        'available_orders': available_orders,
        'completed_orders': completed_orders,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Проверка прав
    if request.user.role == 'client' and order.appointment.user != request.user:
        messages.error(request, 'Доступ запрещён')
        return redirect('home')
    if request.user.role == 'mechanic' and order.mechanic != request.user:
        messages.error(request, 'Этот заказ не назначен вам')
        return redirect('mechanic_dashboard')

    checklist_items = order.checklist_items.all()
    photos = order.photos.all()
    parts = order.parts.all()

    # Проверка, можно ли редактировать заказ (не завершён и не отменён)
    is_editable = order.status not in ['completed', 'cancelled']

    if request.method == 'POST' and request.user.role in ['mechanic', 'owner', 'admin']:
        action = request.POST.get('action')

        # Запрещаем действия, если заказ завершён
        if order.status in ['completed', 'cancelled']:
            messages.error(request, 'Нельзя изменить завершённый или отменённый заказ')
            return redirect('order_detail', order_id=order.id)

        if action == 'start':
            order.status = 'in_progress'
            order.started_at = timezone.now()
            order.save()
            messages.success(request, 'Работы начаты')

        elif action == 'complete':
            order.status = 'completed'
            order.completed_at = timezone.now()
            # Подсчёт итоговой суммы (услуги + запчасти)
            services_total = sum(service.price for service in order.appointment.services.all())
            parts_total = sum(p.total_price for p in parts)
            order.total_amount = services_total + parts_total
            order.save()
            messages.success(request, 'Заказ завершён!')

        elif action == 'add_part':
            if is_editable:
                form = PartForm(request.POST)
                if form.is_valid():
                    part = form.save(commit=False)
                    part.order = order
                    part.save()
                    messages.success(request, f'Добавлена запчасть: {part.name}')
            else:
                messages.error(request, 'Нельзя добавить запчасть в завершённый заказ')

        return redirect('order_detail', order_id=order.id)

    # Подсчёт итоговой суммы для отображения
    services_total = sum(service.price for service in order.appointment.services.all())
    parts_total = sum(p.total_price for p in parts)
    total_amount = services_total + parts_total

    part_form = PartForm()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'checklist_items': checklist_items,
        'photos': photos,
        'parts': parts,
        'part_form': part_form,
        'is_editable': is_editable,
        'services_total': services_total,
        'parts_total': parts_total,
        'total_amount': total_amount,
    })


@login_required
def toggle_checklist(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ChecklistItem, id=item_id)
        order = item.order

        # Проверка прав
        if request.user.role not in ['mechanic', 'owner', 'admin']:
            return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)

        if order.mechanic != request.user and request.user.role not in ['owner', 'admin']:
            return JsonResponse({'status': 'error', 'message': 'Этот заказ не назначен вам'}, status=403)

        # Запрещаем изменение чек-листа, если заказ завершён или отменён
        if order.status in ['completed', 'cancelled']:
            return JsonResponse({'status': 'error', 'message': 'Нельзя изменить завершённый или отменённый заказ'},
                                status=403)

        item.is_completed = not item.is_completed
        item.save()
        return JsonResponse({'status': 'ok', 'is_completed': item.is_completed})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def upload_photo(request, order_id):
    if request.method == 'POST' and request.FILES.get('photo'):
        order = get_object_or_404(Order, id=order_id)

        # Проверка прав
        if request.user.role not in ['mechanic', 'owner', 'admin']:
            messages.error(request, 'Нет прав для загрузки фото')
            return redirect('order_detail', order_id=order.id)

        if order.mechanic != request.user and request.user.role not in ['owner', 'admin']:
            messages.error(request, 'Этот заказ не назначен вам')
            return redirect('order_detail', order_id=order.id)

        # Запрещаем загрузку фото, если заказ завершён или отменён
        if order.status in ['completed', 'cancelled']:
            messages.error(request, 'Нельзя добавить фото в завершённый или отменённый заказ')
            return redirect('order_detail', order_id=order.id)

        PhotoReport.objects.create(
            order=order,
            image=request.FILES['photo'],
            comment=request.POST.get('comment', '')
        )
        messages.success(request, 'Фото загружено')

    return redirect('order_detail', order_id=order_id)


@login_required
def take_order(request, order_id):
    """Механик берёт заказ в работу"""
    order = get_object_or_404(Order, id=order_id, mechanic__isnull=True, status='new')

    if request.user.role != 'mechanic':
        messages.error(request, 'Только механик может взять заказ')
        return redirect('mechanic_dashboard')

    order.mechanic = request.user
    order.is_mechanic_assigned = True
    order.save()

    messages.success(request, f'Вы взяли заказ #{order_id} в работу!')
    return redirect('order_detail', order_id=order.id)


@login_required
def start_order(request, order_id):
    """Механик начинает выполнение заказа"""
    order = get_object_or_404(Order, id=order_id, mechanic=request.user, status='new')

    order.status = 'in_progress'
    order.started_at = timezone.now()
    order.save()

    messages.success(request, 'Работы начаты!')
    return redirect('order_detail', order_id=order.id)
