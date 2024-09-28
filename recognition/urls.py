from django.urls import path
from . import views

app_name = 'recognition'

urlpatterns = [
    path('', views.home, name='home'),
    path('video-feed/', views.video_feed, name='video_feed'),
]
