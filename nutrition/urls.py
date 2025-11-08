from django.urls import path
from . import views

urlpatterns = [
    path('upload-meal/', views.UserUploadedMealCreateView.as_view(), name='upload-meal'),
]