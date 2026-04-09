from django.db import models
from django.conf import settings
from appointments.models import Appointment

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    )
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_mechanic_assigned = models.BooleanField(default=False)

    def __str__(self):
        return f"Заказ #{self.id} - {self.status}"

class ChecklistItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='checklist_items')
    task_name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name

class PhotoReport(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    comment = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Part(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=(('online_card', 'Карта онлайн'), ('cash', 'Наличные')))
    status = models.CharField(max_length=20, choices=(('pending', 'Ожидает'), ('paid', 'Оплачен'), ('failed', 'Ошибка')))
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def create_checklist_for_order(sender, instance, created, **kwargs):
    if created:
        for service in instance.appointment.services.all():
            for task in service.get_checklist_items_list():
                ChecklistItem.objects.create(order=instance, task_name=task)