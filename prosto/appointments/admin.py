# appointments/admin.py
from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('user__username', 'vehicle__license_plate')
    raw_id_fields = ('user', 'vehicle')
    filter_horizontal = ('services',)
    list_editable = ('status',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'vehicle', 'services', 'status')
        }),
        ('Дата и время', {
            'fields': ('date', 'time')
        }),
        ('Системные поля', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)