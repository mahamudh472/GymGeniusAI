from django.contrib import admin
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity,
    CustomRoutine, CustomRoutineExercise, CustomRoutineExerciseCompletion, ExerciseVideo
)
from unfold.admin import ModelAdmin, TabularInline
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin, ImportExportMixin 


# class ExerciseResource(ModelResource):
#     class Meta:
#         model = Exercise

class ExerciseVideoInline(TabularInline):
    model = ExerciseVideo
    extra = 1
    max_num = 5
    readonly_fields = ['uploaded_at']

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_per_page = 50


@admin.register(Exercise)
class ExerciseAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['name', 'muscle_group', 'category', 'difficulty', 'default_sets', 'default_reps', 'equipment_needed']
    list_filter = ['difficulty', 'category', 'muscle_group']
    search_fields = ['name', 'description', 'muscle_group', 'equipment_needed']
    ordering = ['name']
    raw_id_fields = ['category']
    list_per_page = 50
    inlines = [ExerciseVideoInline]
    # resource_class = ExerciseResource
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'video', 'category')
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


class UserExerciseInline(admin.TabularInline):
    model = UserExercise
    extra = 0
    max_num = 20
    fields = ['exercise', 'sets', 'reps', 'duration_seconds', 'rest_time', 'order', 'notes']
    ordering = ['order']
    raw_id_fields = ['exercise']


@admin.register(UserWorkout)
class UserWorkoutAdmin(ModelAdmin):
    list_display = ['name', 'user', 'difficulty', 'created_by_ai', 'is_active', 'estimated_duration', 'estimated_calories', 'created_at']
    list_filter = ['created_by_ai', 'is_active', 'difficulty', 'created_at']
    search_fields = ['name', 'user__email', 'description']
    inlines = [UserExerciseInline]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    list_per_page = 50
    list_select_related = ['user']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'image')
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserExercise)
class UserExerciseAdmin(ModelAdmin):
    list_display = ['user_workout', 'exercise', 'sets', 'reps', 'rest_time', 'order']
    list_filter = ['user_workout__user', 'exercise__difficulty']
    search_fields = ['user_workout__name', 'exercise__name', 'user_workout__user__email']
    ordering = ['user_workout', 'order']
    raw_id_fields = ['exercise', 'user_workout']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('exercise', 'user_workout', 'user_workout__user')


@admin.register(WorkoutProgress)
class WorkoutProgressAdmin(ModelAdmin):
    list_display = ['user_workout', 'completed_at', 'completion_percentage', 'actual_duration', 'actual_calories', 'rating']
    list_filter = ['completed_at', 'rating', 'difficulty_rating']
    search_fields = ['user_workout__user__email', 'user_workout__name']
    ordering = ['-completed_at']
    readonly_fields = ['completed_at', 'completion_percentage']
    raw_id_fields = ['user_workout']
    list_per_page = 50
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_workout', 'user_workout__user')


@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ['user', 'name', 'duration', 'calories', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    list_per_page = 50
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'name')
        }),
        ('Metrics', {
            'fields': ('duration', 'calories')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class CustomRoutineExerciseInline(admin.TabularInline):
    model = CustomRoutineExercise
    extra = 0
    max_num = 20
    fields = ['exercise', 'sets', 'reps', 'duration_seconds', 'rest_time', 'order', 'notes']
    ordering = ['order', 'added_at']
    raw_id_fields = ['exercise']


@admin.register(CustomRoutine)
class CustomRoutineAdmin(ModelAdmin):
    list_display = ['user', 'name', 'created_at', 'updated_at']
    search_fields = ['user__email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CustomRoutineExerciseInline]
    raw_id_fields = ['user']
    list_per_page = 50
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CustomRoutineExercise)
class CustomRoutineExerciseAdmin(ModelAdmin):
    list_display = ['custom_routine', 'exercise', 'sets', 'reps', 'rest_time', 'order', 'added_at']
    list_filter = ['custom_routine__user', 'exercise__difficulty']
    search_fields = ['custom_routine__name', 'exercise__name', 'custom_routine__user__email']
    ordering = ['custom_routine', 'order', 'added_at']
    raw_id_fields = ['exercise', 'custom_routine']
    readonly_fields = ['added_at']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('exercise', 'custom_routine', 'custom_routine__user')


@admin.register(CustomRoutineExerciseCompletion)
class CustomRoutineExerciseCompletionAdmin(ModelAdmin):
    list_display = ['user', 'exercise_name', 'actual_sets', 'actual_reps', 'duration_minutes', 'calories_burned', 'completed_at']
    list_filter = ['completed_at', 'difficulty_rating', 'user']
    search_fields = ['user__email', 'custom_routine_exercise__exercise__name']
    ordering = ['-completed_at']
    readonly_fields = ['completed_at', 'calories_burned']
    raw_id_fields = ['user', 'custom_routine_exercise']
    list_per_page = 50
    
    def exercise_name(self, obj):
        return obj.custom_routine_exercise.exercise.name
    exercise_name.short_description = 'Exercise'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'custom_routine_exercise', 'custom_routine_exercise__exercise')
    
    fieldsets = (
        ('Exercise Information', {
            'fields': ('user', 'custom_routine_exercise', 'completed_at')
        }),
        ('Performance', {
            'fields': ('actual_sets', 'actual_reps', 'actual_duration_seconds')
        }),
        ('Metrics', {
            'fields': ('duration_minutes', 'calories_burned')
        }),
        ('Feedback', {
            'fields': ('difficulty_rating', 'notes')
        }),
    )
