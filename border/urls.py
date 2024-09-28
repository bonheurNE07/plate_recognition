from django.urls import path
from . import views


app_name = 'border'

urlpatterns = [
    path('vehicle/create/', views.vehicle_create, name='vehicle-create'),
    path('', views.vehicle_list, name='vehicle-list'),
    path('vehicle/update/<int:pk>/', views.vehicle_update, name='vehicle-update'),
    path('vehicle/delete/<int:pk>/', views.vehicle_delete, name='vehicle-delete'),

    path('license-plates/', views.list_license_plate, name='license-plate-list'),
    path('license-plate/create/', views.create_license_plate, name='license-plate-create'),
    path('license-plate/update/<int:pk>/', views.update_license_plate, name='license-plate-update'),
    path('license-plate/delete/<int:pk>/', views.delete_license_plate, name='license-plate-delete'),

    path('border-checks/', views.list_border_check, name='border-check-list'),
    path('border-check/create/', views.create_border_check, name='border-check-create'),
    path('border-check/update/<int:pk>/', views.update_border_check, name='border-check-update'),
    path('border-check/delete/<int:pk>/', views.delete_border_check, name='border-check-delete'),

]