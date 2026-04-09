# services/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Service


def is_owner_or_admin(user):
    return user.role in ['owner', 'admin'] or user.is_staff


@login_required
@user_passes_test(is_owner_or_admin)
def service_list(request):
    """Список всех услуг"""
    services = Service.objects.all().order_by('-is_active', 'name')
    return render(request, 'services/service_list.html', {'services': services})


@login_required
@user_passes_test(is_owner_or_admin)
def service_create(request):
    """Создание новой услуги"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_minutes = request.POST.get('duration_minutes', 60)
        is_active = request.POST.get('is_active') == 'on'
        checklist_items = request.POST.get('checklist_items', '')

        if not name or not price:
            messages.error(request, 'Название и цена обязательны')
            return render(request, 'services/service_form.html')

        service = Service.objects.create(
            name=name,
            description=description,
            price=price,
            duration_minutes=duration_minutes,
            is_active=is_active,
            checklist_items=checklist_items
        )

        messages.success(request, f'Услуга "{service.name}" успешно создана!')
        return redirect('service_list')

    return render(request, 'services/service_form.html')


@login_required
@user_passes_test(is_owner_or_admin)
def service_edit(request, service_id):
    """Редактирование услуги"""
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.duration_minutes = request.POST.get('duration_minutes', 60)
        service.is_active = request.POST.get('is_active') == 'on'
        service.checklist_items = request.POST.get('checklist_items', '')
        service.save()

        messages.success(request, f'Услуга "{service.name}" обновлена!')
        return redirect('service_list')

    return render(request, 'services/service_form.html', {'service': service})


@login_required
@user_passes_test(is_owner_or_admin)
def service_delete(request, service_id):
    """Удаление услуги"""
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service_name = service.name
        service.delete()
        messages.success(request, f'Услуга "{service_name}" удалена!')
        return redirect('service_list')

    return render(request, 'services/service_confirm_delete.html', {'service': service})


@login_required
@user_passes_test(is_owner_or_admin)
def service_toggle_active(request, service_id):
    """Включение/выключение услуги"""
    service = get_object_or_404(Service, id=service_id)
    service.is_active = not service.is_active
    service.save()

    status = "активирована" if service.is_active else "деактивирована"
    messages.success(request, f'Услуга "{service.name}" {status}!')
    return redirect('service_list')