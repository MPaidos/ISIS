from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm
from orders.models import Order
from accounts.models import User
from services.bitrix24 import Bitrix24API


@login_required
def booking(request):
    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут записываться на сервис')
        return redirect('home')

    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = 'pending'
            appointment.save()
            form.save_m2m()  # сохраняем ManyToMany (services)

            try:
                bitrix = Bitrix24API()

                # Проверяем, есть ли уже контакт
                result = bitrix.find_contact_by_phone(request.user.phone)
                contact_id = None

                if result.get('result'):
                    contact_id = result['result'][0]['ID']
                else:
                    # Создаём новый контакт
                    contact_result = bitrix.create_contact(request.user)
                    if contact_result.get('result'):
                        contact_id = contact_result['result']

                # Создаём сделку
                if contact_id:
                    deal_result = bitrix.create_deal(appointment, contact_id)
                    if deal_result.get('result'):
                        print(f"Создана сделка в Битрикс24: {deal_result['result']}")
                    else:
                        print(f"Ошибка создания сделки: {deal_result}")
            except Exception as e:
                print(f"Bitrix24 integration error: {e}")

            messages.success(request, f'Запись создана! Ожидайте подтверждения. ID: {appointment.id}')
            return redirect('appointment_confirmation', appointment_id=appointment.id)
    else:
        form = AppointmentForm(request.user)

    return render(request, 'appointments/booking.html', {'form': form})


@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    return render(request, 'appointments/confirmation.html', {'appointment': appointment})


@staff_member_required
def confirm_appointment(request, appointment_id):
    """Подтверждение записи владельцем/админом"""
    appointment = get_object_or_404(Appointment, id=appointment_id, status='pending')

    if request.method == 'POST':
        appointment.status = 'confirmed'
        appointment.save()

        # Создаём заказ
        order = Order.objects.create(
            appointment=appointment,
            mechanic=request.user if request.user.role == 'mechanic' else None,
            status='new'
        )

        messages.success(request, f'Запись #{appointment_id} подтверждена! Создан заказ #{order.id}')

        # Отправляем уведомление клиенту
        # TODO: добавить push-уведомление

        return redirect('appointment_confirmation', appointment_id=appointment.id)

    return render(request, 'appointments/confirm.html', {'appointment': appointment})

@staff_member_required
def pending_appointments(request):
    """Список записей, ожидающих подтверждения (для владельца)"""
    appointments = Appointment.objects.filter(status='pending').select_related('user', 'vehicle')
    return render(request, 'appointments/pending_list.html', {'appointments': appointments})


def is_owner_or_admin(user):
    return user.role in ['owner', 'admin'] or user.is_staff


@login_required
@user_passes_test(is_owner_or_admin)
def pending_appointments(request):
    """Список записей, ожидающих подтверждения (для владельца)"""
    appointments = Appointment.objects.filter(status='pending').select_related('user', 'vehicle')
    return render(request, 'appointments/pending_list.html', {'appointments': appointments})


@login_required
@user_passes_test(is_owner_or_admin)
def confirm_appointment(request, appointment_id):
    """Подтверждение записи владельцем с возможностью назначить механика"""
    appointment = get_object_or_404(Appointment, id=appointment_id, status='pending')
    mechanics = User.objects.filter(role='mechanic', is_active=True)

    if request.method == 'POST':
        mechanic_id = request.POST.get('mechanic_id')
        appointment.status = 'confirmed'
        appointment.save()

        # Создаём заказ
        order = Order.objects.create(
            appointment=appointment,
            mechanic_id=mechanic_id if mechanic_id else None,
            status='new',
            is_mechanic_assigned=bool(mechanic_id)
        )

        messages.success(request, f'Запись #{appointment_id} подтверждена! Создан заказ #{order.id}')
        return redirect('pending_appointments')

    return render(request, 'appointments/confirm_appointment.html', {
        'appointment': appointment,
        'mechanics': mechanics
    })


@login_required
def my_orders(request):
    """Список всех заказов клиента (активные + завершённые)"""
    if request.user.role != 'client':
        messages.error(request, 'Доступ запрещён')
        return redirect('home')

    # Получаем все записи клиента
    appointments = Appointment.objects.filter(user=request.user).order_by('-created_at')

    # Для каждой записи получаем связанный заказ (если есть)
    orders_data = []
    for appointment in appointments:
        try:
            order = Order.objects.get(appointment=appointment)
            # Определяем статус для отображения
            # Если заказ завершён, показываем статус заказа
            # Если заказ в процессе, показываем статус заказа
            # Если заказ новый, но запись подтверждена - показываем "Подтверждён"
            if order.status == 'new' and appointment.status == 'confirmed':
                display_status = 'confirmed'
            else:
                display_status = order.status

            orders_data.append({
                'appointment': appointment,
                'order': order,
                'has_order': True,
                'display_status': display_status
            })
        except Order.DoesNotExist:
            orders_data.append({
                'appointment': appointment,
                'order': None,
                'has_order': False,
                'display_status': appointment.status
            })

    # Статистика
    stats = {
        'total': len(orders_data),
        'pending': sum(1 for item in orders_data if item['display_status'] in ['pending', 'new']),
        'in_progress': sum(1 for item in orders_data if item['display_status'] in ['confirmed', 'in_progress']),
        'completed': sum(1 for item in orders_data if item['display_status'] == 'completed'),
    }

    # Фильтр по статусу
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'pending':
        orders_data = [item for item in orders_data if item['display_status'] in ['pending', 'new']]
    elif status_filter == 'active':
        orders_data = [item for item in orders_data if item['display_status'] in ['confirmed', 'in_progress']]
    elif status_filter == 'completed':
        orders_data = [item for item in orders_data if item['display_status'] == 'completed']

    return render(request, 'appointments/my_orders.html', {
        'orders_data': orders_data,
        'stats': stats,
        'current_filter': status_filter,
    })


@login_required
def order_status(request, order_id):
    """Детальная информация о статусе конкретного заказа"""
    if request.user.role != 'client':
        messages.error(request, 'Доступ запрещён')
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, appointment__user=request.user)
    appointment = order.appointment

    # Определяем статус для отображения
    if order.status == 'new' and appointment.status == 'confirmed':
        display_status = 'confirmed'
    else:
        display_status = order.status

    # Получаем фотоотчёт (если есть)
    photos = order.photos.all()

    # Получаем запчасти
    parts = order.parts.all()

    # Подсчёт сумм
    services_total = sum(service.price for service in appointment.services.all())
    parts_total = sum(part.total_price for part in parts)
    total_amount = services_total + parts_total

    # Статусы с человеко-читаемыми названиями и иконками
    status_info = {
        'pending': {'name': 'Ожидает подтверждения', 'icon': '⏰', 'color': 'status-pending', 'step': 1},
        'new': {'name': 'Ожидает подтверждения', 'icon': '⏰', 'color': 'status-pending', 'step': 1},
        'confirmed': {'name': 'Подтверждён, ожидает начала', 'icon': '✅', 'color': 'status-confirmed', 'step': 2},
        'in_progress': {'name': 'В работе', 'icon': '🔧', 'color': 'status-in_progress', 'step': 3},
        'completed': {'name': 'Завершён', 'icon': '🎉', 'color': 'status-completed', 'step': 4},
        'cancelled': {'name': 'Отменён', 'icon': '❌', 'color': 'status-cancelled', 'step': 0},
    }

    current_status = status_info.get(display_status, status_info['pending'])

    return render(request, 'appointments/order_status.html', {
        'order': order,
        'appointment': appointment,
        'photos': photos,
        'parts': parts,
        'services_total': services_total,
        'parts_total': parts_total,
        'total_amount': total_amount,
        'order_status': current_status,
        'status_info': status_info,
    })