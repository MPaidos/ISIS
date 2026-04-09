# vehicles/admin.py
from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'brand', 'model', 'year', 'license_plate')
    list_filter = ('brand', 'year')
    search_fields = ('brand', 'model', 'license_plate', 'owner__username')
    raw_id_fields = ('owner',)