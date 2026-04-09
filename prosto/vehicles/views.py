from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        Vehicle.objects.create(
            owner=request.user,
            brand=request.POST.get('brand'),
            model=request.POST.get('model'),
            year=request.POST.get('year') or 2000,
            license_plate=request.POST.get('license_plate', ''),
            vin=request.POST.get('vin', ''),
            mileage=request.POST.get('mileage', 0),
        )
        messages.success(request, 'Автомобиль добавлен')
    return redirect('profile')