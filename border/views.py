from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django import forms

from .models import Vehicle, LicensePlate, BorderCheck


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_model', 'vehicle_color', 'owner_name', 'country_of_origin', 'destination_country', 'vehicle_photo']
        widgets = {
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_color': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country_of_origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_country': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class LicensePlateForm(forms.ModelForm):
    class Meta:
        model = LicensePlate
        fields = ['vehicle', 'license_plate_number', 'license_plate_image', 'issued_at']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for selecting the vehicle
            'license_plate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter license plate number'}),
            'license_plate_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'issued_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class BorderCheckForm(forms.ModelForm):
    class Meta:
        model = BorderCheck
        fields = ['vehicle', 'border_name', 'authorization_file']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}), 
            'border_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter The border Name'}),
            'authorization_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('border:vehicle-list')
    else:
        form = VehicleForm()

    return render(request, 'border/vehicle_create.html', {'form': form})



def vehicle_list(request):
    query = request.GET.get('search')
    if query:
        vehicles = Vehicle.objects.filter(
            models.Q(owner_name__icontains=query) | 
            models.Q(vehicle_model__icontains=query)
        )
    else:
        vehicles = Vehicle.objects.all()

    return render(request, 'border/vehicle_list.html', {'vehicles': vehicles, 'search_query': query})

def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('border:vehicle-list')
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'border/vehicle_update.html', {'form': form, 'vehicle': vehicle})


def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        return redirect('border:vehicle-list')
    return render(request, 'border/vehicle_delete.html', {'vehicle': vehicle})



def create_license_plate(request):
    if request.method == 'POST':
        form = LicensePlateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('border:license-plate-list')
    else:
        form = LicensePlateForm()
    
    return render(request, 'border/license_plate_create.html', {'form': form})


def list_license_plate(request):
    query = request.GET.get('search')
    if query:
        license_plates = LicensePlate.objects.filter(
            models.Q(license_plate_number__icontains=query)
        )
    else:
        license_plates = LicensePlate.objects.all()
    return render(request, 'border/license_plate_list.html', {'license_plates': license_plates, 'search_query': query})


def update_license_plate(request, pk):
    license_plate = get_object_or_404(LicensePlate, pk=pk)
    
    if request.method == 'POST':
        form = LicensePlateForm(request.POST, request.FILES, instance=license_plate)
        if form.is_valid():
            form.save()
            return redirect('border:license-plate-list')
    else:
        form = LicensePlateForm(instance=license_plate)
    
    return render(request, 'border/license_plate_update.html', {'form': form, 'license_plate': license_plate})

def delete_license_plate(request, pk):
    license_plate = get_object_or_404(LicensePlate, pk=pk)
    
    if request.method == 'POST':
        license_plate.delete()
        return redirect('border:license-plate-list')
    
    return render(request, 'border/license_plate_delete.html', {'license_plate': license_plate})


def create_border_check(request):
    if request.method == 'POST':
        form = BorderCheckForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('border:border-check-list')
    else:
        form = BorderCheckForm()
    
    return render(request, 'border/border_check_create.html', {'form': form})

def list_border_check(request):
    border_checks = BorderCheck.objects.all()
    return render(request, 'border/border_check_list.html', {'border_checks': border_checks})


def update_border_check(request, pk):
    border_check = get_object_or_404(BorderCheck, pk=pk)
    
    if request.method == 'POST':
        form = BorderCheckForm(request.POST, request.FILES, instance=border_check)
        if form.is_valid():
            form.save()
            return redirect('border:border-check-list')
    else:
        form = BorderCheckForm(instance=border_check)
    
    return render(request, 'border/border_check_update.html', {'form': form, 'border_check': border_check})


def delete_border_check(request, pk):
    border_check = get_object_or_404(BorderCheck, pk=pk)
    
    if request.method == 'POST':
        border_check.delete()
        return redirect('border:border-check-list')
    
    return render(request, 'border/border_check_delete.html', {'border_check': border_check})
