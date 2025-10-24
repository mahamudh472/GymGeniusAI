from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.WorkoutListCreateView.as_view(), name='workout-list'),
    path('<int:pk>/', views.WorkoutDetailView.as_view(), name='workout-detail'),
    path('categories/', views.WorkoutCategoryListCreateView.as_view(), name='workout-category-list'),
    path('categories/<int:pk>/', views.WorkoutCategoryDetailView.as_view(), name='workout-category-detail'),
    path('user-progress/', views.UserWorkoutProgressListCreateView.as_view(), name='user-workout-progress-list'),
    path('user-progress/<int:pk>/', views.UserWorkoutProgressDetailView.as_view(), name='user-workout-progress-detail'),
]   