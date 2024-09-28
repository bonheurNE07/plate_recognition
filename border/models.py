from django.db import models
import fitz  # PyMuPDF
from django.core.files.storage import default_storage

class Vehicle(models.Model):
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    owner_name = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=50)
    destination_country = models.CharField(max_length=50)
    vehicle_photo = models.ImageField(upload_to='vehicle_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle_model} - {self.owner_name}"


class LicensePlate(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='license_plates')
    license_plate_number = models.CharField(max_length=20)
    license_plate_image = models.ImageField(upload_to='license_plates/', blank=True, null=True)
    issued_at = models.DateField()

    def __str__(self):
        return self.license_plate_number


class BorderCheck(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='border_checks')
    border_name = models.CharField(max_length=100)
    checked_at = models.DateTimeField(auto_now_add=True)
    authorization_file = models.FileField(upload_to='authorization_docs/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If an authorization file is uploaded, check for the specific pattern
        if self.authorization_file:
            # Save the instance first to get the file path
            super().save(*args, **kwargs)
            # Check file authorization status
            self.is_approved = self.check_authorization_file(self.authorization_file)
            # Update the instance again with the approval status
            super().save(update_fields=['is_approved'])
        else:
            super().save(*args, **kwargs)

    def check_authorization_file(self, file):
        """
        This method reads the uploaded PDF file and checks if the specific pattern is found.
        If the pattern is found, the vehicle will be approved.
        """
        specific_pattern = "AUTHORIZED TO PASS"  # Define your pattern here

        try:
            # Ensure file exists and is of correct type
            file_path = default_storage.path(file.name)
            if not file_path.lower().endswith('.pdf'):
                return False

            # Open and read the PDF file
            doc = fitz.open(file_path)
            full_text = []
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                full_text.append(page.get_text())
            document_text = '\n'.join(full_text)
            doc.close()
            
            # Check if the pattern is in the document
            if specific_pattern in document_text:
                return True
        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Error reading file: {e}")

        return False

    def __str__(self):
        return f"Border Check for {self.vehicle} at {self.border_name} on {self.checked_at}"
