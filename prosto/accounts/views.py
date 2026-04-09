from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import User


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'client')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'core/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'core/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        user.phone = phone
        user.save()

        login(request, user)
        messages.success(request, f'Добро пожаловать, {username}!')

        if role == 'mechanic':
            return redirect('mechanic_dashboard')
        return redirect('home')

    return render(request, 'core/register.html')

def custom_logout(request):
    """Выход из системы (поддерживает GET и POST)"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')