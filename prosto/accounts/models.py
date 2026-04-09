from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('mechanic', 'Механик'),
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    push_token = models.CharField(max_length=255, blank=True, verbose_name='Push-токен')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"