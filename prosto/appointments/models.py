from django.db import models
from django.conf import settings
from vehicles.models import Vehicle
from services.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    date = models.DateField(verbose_name='Дата')
    time = models.CharField(max_length=10, verbose_name='Время')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Запись #{self.id} - {self.user.username} - {self.date} {self.time}"