from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    duration_minutes = models.IntegerField(default=60, verbose_name='Длительность (мин)')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    checklist_items = models.TextField(
        blank=True,
        verbose_name='Пункты чек-листа',
        help_text='Каждый пункт с новой строки'
    )

    def __str__(self):
        return f"{self.name} - {self.price} ₽"

    def get_checklist_items_list(self):
        """Возвращает список пунктов чек-листа"""
        if self.checklist_items:
            return [item.strip() for item in self.checklist_items.split('\n') if item.strip()]
        return ['Выполнить работу', 'Проверить качество']