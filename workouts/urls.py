from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'exercise-categories', views.ExerciseCategoryViewSet, basename='exercise-category')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')
router.register(r'user-workouts', views.UserWorkoutViewSet, basename='user-workout')
router.register(r'user-exercises', views.UserExerciseViewSet, basename='user-exercise')
router.register(r'progress', views.WorkoutProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
]