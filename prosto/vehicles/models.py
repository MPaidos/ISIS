from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    brand = models.CharField(max_length=50, verbose_name='Марка')
    model = models.CharField(max_length=50, verbose_name='Модель')
    year = models.IntegerField(verbose_name='Год выпуска')
    license_plate = models.CharField(max_length=20, verbose_name='Госномер')
    vin = models.CharField(max_length=17, blank=True, verbose_name='VIN')
    mileage = models.IntegerField(default=0, verbose_name='Пробег')

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"