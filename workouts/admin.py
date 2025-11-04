from django.contrib import admin
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress
)
from unfold.admin import ModelAdmin


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Exercise)
class ExerciseAdmin(ModelAdmin):
    list_display = ['name', 'muscle_group', 'category', 'difficulty', 'default_sets', 'default_reps', 'equipment_needed']
    list_filter = ['difficulty', 'category', 'muscle_group']
    search_fields = ['name', 'description', 'muscle_group', 'equipment_needed']
    ordering = ['name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'video_url', 'category')
        }),
        ('Classification', {
            'fields': ('muscle_group', 'difficulty', 'equipment_needed')
        }),
        ('Default Parameters', {
            'fields': ('default_sets', 'default_reps', 'default_duration_seconds', 'default_rest_time')
        }),
        ('Metadata', {
            'fields': ('calories_per_rep', 'tips')
        }),
    )


class UserExerciseInline(admin.TabularInline):
    model = UserExercise
    extra = 1
    fields = ['exercise', 'sets', 'reps', 'duration_seconds', 'rest_time', 'order', 'notes']
    ordering = ['order']
    autocomplete_fields = ['exercise']


@admin.register(UserWorkout)
class UserWorkoutAdmin(ModelAdmin):
    list_display = ['name', 'user', 'difficulty', 'created_by_ai', 'is_active', 'estimated_duration', 'estimated_calories', 'created_at']
    list_filter = ['created_by_ai', 'is_active', 'difficulty', 'created_at']
    search_fields = ['name', 'user__email', 'description']
    inlines = [UserExerciseInline]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Workout Details', {
            'fields': ('difficulty', 'created_by_ai', 'is_active')
        }),
        ('Estimates', {
            'fields': ('estimated_duration', 'estimated_calories'),
            'description': 'These are calculated automatically based on exercises'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserExercise)
class UserExerciseAdmin(ModelAdmin):
    list_display = ['user_workout', 'exercise', 'sets', 'reps', 'rest_time', 'order']
    list_filter = ['user_workout__user', 'exercise__difficulty']
    search_fields = ['user_workout__name', 'exercise__name', 'user_workout__user__email']
    ordering = ['user_workout', 'order']
    autocomplete_fields = ['exercise', 'user_workout']


@admin.register(WorkoutProgress)
class WorkoutProgressAdmin(ModelAdmin):
    list_display = ['user_workout', 'completed_at', 'completion_percentage', 'actual_duration', 'actual_calories', 'rating']
    list_filter = ['completed_at', 'rating', 'difficulty_rating']
    search_fields = ['user_workout__user__email', 'user_workout__name']
    ordering = ['-completed_at']
    readonly_fields = ['completed_at', 'completion_percentage']
    fieldsets = (
        ('Workout Information', {
            'fields': ('user_workout', 'completed_at')
        }),
        ('Completion Details', {
            'fields': ('completed_exercises', 'completion_percentage')
        }),
        ('Actual Metrics', {
            'fields': ('actual_duration', 'actual_calories')
        }),
        ('Feedback', {
            'fields': ('rating', 'difficulty_rating', 'notes')
        }),
    )
