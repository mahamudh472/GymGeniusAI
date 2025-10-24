from django.contrib import admin
from .models import WorkoutCategory, Workout, WorkoutRound, Exercise, UserWorkoutProgress


@admin.register(WorkoutCategory)
class WorkoutCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'duration_minutes', 'calories_burn']
    list_filter = ['difficulty', 'category']
    search_fields = ['title', 'description']


@admin.register(WorkoutRound)
class WorkoutRoundAdmin(admin.ModelAdmin):
    list_display = ['workout', 'name', 'round_order']
    list_filter = ['workout']
    search_fields = ['workout__title', 'name']
    ordering = ['workout', 'round_order']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'round', 'reps', 'sets', 'rest_seconds']
    list_filter = ['round__workout']
    search_fields = ['name', 'tips']


@admin.register(UserWorkoutProgress)
class UserWorkoutProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'date', 'calories_burned', 'duration_minutes']
    list_filter = ['date', 'workout']
    search_fields = ['user__email', 'workout__title']
    ordering = ['-date']
