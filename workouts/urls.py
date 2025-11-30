from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'


urlpatterns = [
    path('', views.UserWorkoutListAPIView.as_view(), name='user-workouts'),
    path('<int:pk>/', views.UserWorkoutDetailAPIView.as_view(), name='user-workout-detail'),
    path('track-progress/', views.TrackWorkoutProgressView.as_view(), name='track-workout-progress'),
    path('activities/', views.ActivityListView.as_view(), name='activity-list'),
    path('daily-progress/', views.DailyProgressView.as_view(), name='daily-progress'),
    
    # Exercise listing
    path('exercises/', views.ExerciseListView.as_view(), name='exercise-list'),
    
    # Custom routine endpoints
    path('custom-routine/', views.CustomRoutineView.as_view(), name='custom-routine'),
    path('custom-routine/toggle-exercise/', views.ToggleCustomRoutineExerciseView.as_view(), name='toggle-custom-routine-exercise'),
    path('custom-routine/exercises/', views.CustomRoutineExercisesListView.as_view(), name='custom-routine-exercises'),
    path('custom-routine/complete-exercise/', views.CompleteCustomRoutineExerciseView.as_view(), name='complete-custom-routine-exercise'),
    path('custom-routine/completion-history/', views.CustomRoutineExerciseCompletionHistoryView.as_view(), name='custom-routine-completion-history'),
]