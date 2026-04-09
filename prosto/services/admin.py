# services/admin.py
from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_minutes', 'is_active', 'checklist_preview')
    list_editable = ('price', 'duration_minutes', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    fields = ('name', 'description', 'price', 'duration_minutes', 'is_active', 'checklist_items')

    def checklist_preview(self, obj):
        items = obj.get_checklist_items_list()
        if items:
            return ', '.join(items[:3]) + ('...' if len(items) > 3 else '')
        return '—'

    checklist_preview.short_description = 'Чек-лист'