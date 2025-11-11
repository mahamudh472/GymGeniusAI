from django.urls import path
from . import views

urlpatterns = [
    path('', views.NutritionHomeView.as_view(), name='nutrition-home'),
    path('upload-meal/', views.UserUploadedMealCreateView.as_view(), name='upload-meal'),
]