from django.contrib import admin
from .models import Vehicle, LicensePlate, BorderCheck

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_model', 'owner_name', 'country_of_origin', 'destination_country')
    search_fields = ('vehicle_model', 'owner_name', 'country_of_origin', 'destination_country')


@admin.register(LicensePlate)
class LicensePlateAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'license_plate_number', 'issued_at')
    search_fields = ('license_plate_number', 'vehicle__vehicle_model')


@admin.register(BorderCheck)
class BorderCheckAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'border_name', 'checked_at', 'is_approved')
    search_fields = ('vehicle__vehicle_model', 'border_name')
    list_filter = ('is_approved', 'checked_at')
    fields = ('vehicle', 'border_name', 'authorization_file', 'is_approved')  # Added authorization_file field
    readonly_fields = ('is_approved',)  # is_approved field is set based on file content

