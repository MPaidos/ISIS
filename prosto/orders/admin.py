# orders/admin.py
from django.contrib import admin
from .models import Order, ChecklistItem, PhotoReport, Part, Payment


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ('task_name', 'is_completed')


class PartInline(admin.TabularInline):
    model = Part
    extra = 1
    fields = ('name', 'quantity', 'unit_price')


class PhotoReportInline(admin.TabularInline):
    model = PhotoReport
    extra = 1
    fields = ('image', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'mechanic', 'status', 'total_amount', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('appointment__user__username', 'mechanic__username')
    raw_id_fields = ('appointment', 'mechanic')
    inlines = [ChecklistItemInline, PartInline, PhotoReportInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('appointment', 'mechanic', 'status', 'total_amount')
        }),
        ('Время выполнения', {
            'fields': ('started_at', 'completed_at')
        }),
    )


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'task_name', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('task_name', 'order__id')
    raw_id_fields = ('order',)


@admin.register(PhotoReport)
class PhotoReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('order',)
    readonly_fields = ('created_at',)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'name', 'quantity', 'unit_price', 'total_price')
    search_fields = ('name', 'order__id')
    raw_id_fields = ('order',)
    readonly_fields = ('total_price',)

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Итого'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__id', 'transaction_id')
    raw_id_fields = ('order',)
    readonly_fields = ('created_at',)