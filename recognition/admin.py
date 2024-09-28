from django.contrib import admin
from .models import MotorControlLog

@admin.register(MotorControlLog)
class MotorControlLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'action', 'triggered_at')  # Columns to display in the list view
    list_filter = ('action',)  # Filters to add to the admin sidebar
    search_fields = ('vehicle__license_plate_number', 'action')  # Search fields

    def __str__(self):
        return f"{self.action} for Vehicle {self.vehicle} at {self.triggered_at}"
