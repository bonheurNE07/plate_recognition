from django.db import models
from border.models import Vehicle

class PlateRecognition(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    plate_number = models.CharField(max_length=20)
    detected_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False, null=True)
    
    def __str__(self):
        return f"Plate: {self.plate_number}, Detected at {self.detected_at}"

class MotorControlLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50)  # "Open Gate" or "Close Gate"
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} for Vehicle {self.vehicle} at {self.triggered_at}"
