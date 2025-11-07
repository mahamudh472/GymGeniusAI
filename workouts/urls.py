from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'


urlpatterns = [
    path('', views.UserWorkoutListAPIView.as_view(), name='user-workouts'),
    path('<int:pk>/', views.UserWorkoutDetailAPIView.as_view(), name='user-workout-detail'),
    path('generate-workouts/', views.test, name='generate-workouts'),
]