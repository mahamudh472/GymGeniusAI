from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from .models import (
    Rank, ActivityType, UserRank, PointTransaction,
    WeeklyLeaderboard, RankHistory, UserStreak, Challenge, UserChallengeProgress
)
from .forms import ChallengeAdminForm, get_challenge_exercise_formset
from workouts.models import Exercise
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils import timezone


@admin.register(Rank)
class RankAdmin(ModelAdmin):
    list_display = ['name', 'level', 'promotion_threshold', 'demotion_threshold', 'min_points_required', 'color_code']
    list_filter = ['level']
    search_fields = ['name']
    ordering = ['level']
    list_per_page = 50


@admin.register(ActivityType)
class ActivityTypeAdmin(ModelAdmin):
    list_display = ['name', 'code', 'points', 'max_per_day', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50


@admin.register(UserRank)
class UserRankAdmin(ModelAdmin):
    list_display = ['user', 'current_rank', 'total_points', 'weekly_points', 'rank_updated_at']
    list_filter = ['current_rank', 'rank_updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'rank_updated_at']
    ordering = ['-weekly_points', '-total_points']
    raw_id_fields = ['user', 'current_rank', 'highest_rank_achieved']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'current_rank', 'highest_rank_achieved')


@admin.register(PointTransaction)
class PointTransactionAdmin(ModelAdmin):
    list_display = ['user', 'activity_type', 'points', 'description', 'created_at', 'week_start']
    list_filter = ['activity_type', 'created_at', 'week_start']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'activity_type']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'activity_type')


@admin.register(WeeklyLeaderboard)
class WeeklyLeaderboardAdmin(ModelAdmin):
    list_display = ['user', 'rank', 'week_start', 'position_in_rank', 'weekly_points', 'rank_changed']
    list_filter = ['rank', 'week_start', 'rank_changed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'week_start'
    raw_id_fields = ['user', 'rank', 'old_rank']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'rank', 'old_rank')


@admin.register(RankHistory)
class RankHistoryAdmin(ModelAdmin):
    list_display = ['user', 'old_rank', 'new_rank', 'reason', 'weekly_points', 'changed_at']
    list_filter = ['old_rank', 'new_rank', 'changed_at']
    search_fields = ['user__username', 'user__email', 'reason']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
    raw_id_fields = ['user', 'old_rank', 'new_rank']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'old_rank', 'new_rank')


@admin.register(UserStreak)
class UserStreakAdmin(ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_check_in', 'total_check_ins']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_check_in']
    ordering = ['-current_streak']
    raw_id_fields = ['user']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Challenge)
class ChallengeAdmin(ModelAdmin):
    form = ChallengeAdminForm
    change_list_template = 'admin/gamification/challenge_changelist.html'
    list_display = ['name', 'challenge_type', 'difficulty', 'completion_points', 'exercise_count', 'start_date', 'end_date', 'is_active']
    list_filter = ['challenge_type', 'difficulty', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'estimated_duration', 'estimated_calories']
    date_hierarchy = 'start_date'
    raw_id_fields = ['created_by']
    list_per_page = 50
    
    @display(description="Exercises", ordering="id")
    def exercise_count(self, obj):
        """Display number of exercises in the challenge"""
        if obj.exercises:
            count = len(obj.exercises)
            return format_html(
                '<span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 3px; font-weight: 500;">{} exercises</span>',
                count
            )
        return format_html('<span style="color: #999;">No exercises</span>')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'create-challenge/',
                self.admin_site.admin_view(self.create_challenge_view),
                name='gamification_challenge_create'
            ),
            path(
                '<path:object_id>/edit-challenge/',
                self.admin_site.admin_view(self.edit_challenge_view),
                name='gamification_challenge_edit'
            ),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to add custom create button"""
        extra_context = extra_context or {}
        extra_context['custom_create_url'] = reverse('admin:gamification_challenge_create')
        return super().changelist_view(request, extra_context)
    
    def create_challenge_view(self, request):
        """Custom view for creating challenges with exercise formset"""
        ChallengeExerciseFormSet = get_challenge_exercise_formset(extra=3)
        
        if request.method == 'POST':
            form = ChallengeAdminForm(request.POST)
            form.current_user = request.user
            formset = ChallengeExerciseFormSet(request.POST, prefix='exercises')
            
            if form.is_valid() and formset.is_valid():
                challenge = form.save(commit=False)
                challenge.created_by = request.user
                
                # Build exercises JSON from formset
                exercises_data = []
                total_duration = 0
                total_calories = 0
                
                for exercise_form in formset:
                    if exercise_form.cleaned_data and not exercise_form.cleaned_data.get('DELETE', False):
                        exercise = exercise_form.cleaned_data['exercise']
                        sets = exercise_form.cleaned_data['sets']
                        reps = exercise_form.cleaned_data.get('reps')
                        duration_seconds = exercise_form.cleaned_data.get('duration_seconds')
                        rest_time = exercise_form.cleaned_data['rest_time']
                        notes = exercise_form.cleaned_data.get('notes', '')
                        
                        exercise_data = {
                            'exercise_id': exercise.id,
                            'name': exercise.name,
                            'sets': sets,
                            'rest_time': rest_time,
                        }
                        
                        if reps:
                            exercise_data['reps'] = reps
                            # Calculate calories for rep-based exercises
                            total_calories += sets * reps * exercise.calories_per_rep
                            # Estimate duration (3 seconds per rep + rest time)
                            total_duration += sets * (reps * 3 + rest_time)
                        
                        if duration_seconds:
                            exercise_data['duration_seconds'] = duration_seconds
                            # For timed exercises, estimate calories differently
                            if not reps:
                                # Rough estimate: 0.1 calories per second
                                total_calories += sets * duration_seconds * 0.1
                            total_duration += sets * (duration_seconds + rest_time)
                        
                        if notes:
                            exercise_data['notes'] = notes
                        
                        exercises_data.append(exercise_data)
                
                challenge.exercises = exercises_data
                challenge.estimated_duration = int(total_duration / 60)  # Convert to minutes
                challenge.estimated_calories = int(total_calories)
                challenge.save()
                
                messages.success(
                    request, 
                    f'Challenge "{challenge.name}" created successfully with {len(exercises_data)} exercises!'
                )
                return redirect('admin:gamification_challenge_changelist')
        else:
            form = ChallengeAdminForm()
            ChallengeExerciseFormSet = get_challenge_exercise_formset(extra=3)
            formset = ChallengeExerciseFormSet(prefix='exercises')
        
        # Get all admin context
        context = {
            **admin.site.each_context(request),
            'title': 'Create Challenge',
            'form': form,
            'formset': formset,
            'opts': self.model._meta,
            'object': None,
            'add': True,
            'change': False,
            'is_popup': False,
            'save_as': False,
            'has_view_permission': self.has_view_permission(request),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': False,
            'original': None,
        }
        
        return render(request, 'admin/gamification/challenge_form.html', context)
    
    def edit_challenge_view(self, request, object_id):
        """Custom view for editing challenges with exercise formset"""
        try:
            challenge = Challenge.objects.get(pk=object_id)
        except Challenge.DoesNotExist:
            messages.error(request, 'Challenge not found.')
            return redirect('admin:gamification_challenge_changelist')
        
        if request.method == 'POST':
            form = ChallengeAdminForm(request.POST, instance=challenge)
            form.current_user = request.user
            ChallengeExerciseFormSet = get_challenge_exercise_formset(extra=1)
            formset = ChallengeExerciseFormSet(request.POST, prefix='exercises')
            
            if form.is_valid() and formset.is_valid():
                challenge = form.save(commit=False)
                
                # Build exercises JSON from formset
                exercises_data = []
                total_duration = 0
                total_calories = 0
                
                for exercise_form in formset:
                    if exercise_form.cleaned_data and not exercise_form.cleaned_data.get('DELETE', False):
                        exercise = exercise_form.cleaned_data['exercise']
                        sets = exercise_form.cleaned_data['sets']
                        reps = exercise_form.cleaned_data.get('reps')
                        duration_seconds = exercise_form.cleaned_data.get('duration_seconds')
                        rest_time = exercise_form.cleaned_data['rest_time']
                        notes = exercise_form.cleaned_data.get('notes', '')
                        
                        exercise_data = {
                            'exercise_id': exercise.id,
                            'name': exercise.name,
                            'sets': sets,
                            'rest_time': rest_time,
                        }
                        
                        if reps:
                            exercise_data['reps'] = reps
                            total_calories += sets * reps * exercise.calories_per_rep
                            total_duration += sets * (reps * 3 + rest_time)
                        
                        if duration_seconds:
                            exercise_data['duration_seconds'] = duration_seconds
                            if not reps:
                                total_calories += sets * duration_seconds * 0.1
                            total_duration += sets * (duration_seconds + rest_time)
                        
                        if notes:
                            exercise_data['notes'] = notes
                        
                        exercises_data.append(exercise_data)
                
                challenge.exercises = exercises_data
                challenge.estimated_duration = int(total_duration / 60) if total_duration > 0 else 0
                challenge.estimated_calories = int(total_calories) if total_calories > 0 else 0
                challenge.save()
                
                messages.success(
                    request, 
                    f'Challenge "{challenge.name}" updated successfully!'
                )
                return redirect('admin:gamification_challenge_changelist')
        else:
            form = ChallengeAdminForm(instance=challenge)
            
            # Pre-populate formset with existing exercises
            initial_data = []
            extra_forms_needed = 3  # Default extra forms
            
            if challenge.exercises:
                for ex_data in challenge.exercises:
                    exercise_id = ex_data.get('exercise_id')
                    if exercise_id:
                        try:
                            exercise = Exercise.objects.get(id=exercise_id)
                            initial_data.append({
                                'exercise': exercise,
                                'sets': ex_data.get('sets', 3),
                                'reps': ex_data.get('reps'),
                                'duration_seconds': ex_data.get('duration_seconds'),
                                'rest_time': ex_data.get('rest_time', 60),
                                'notes': ex_data.get('notes', ''),
                            })
                        except Exercise.DoesNotExist:
                            pass
                
                # Add extra forms if we have existing data
                extra_forms_needed = max(1, 3 - len(initial_data))
            
            # Create formset with initial data
            ChallengeExerciseFormSet = get_challenge_exercise_formset(extra=extra_forms_needed)
            formset = ChallengeExerciseFormSet(prefix='exercises', initial=initial_data)
        
        # Get all admin context
        context = {
            **admin.site.each_context(request),
            'title': f'Edit Challenge: {challenge.name}',
            'form': form,
            'formset': formset,
            'object': challenge,
            'original': challenge,
            'opts': self.model._meta,
            'add': False,
            'change': True,
            'is_popup': False,
            'save_as': False,
            'has_view_permission': self.has_view_permission(request),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, challenge),
            'has_delete_permission': self.has_delete_permission(request, challenge),
        }
        
        
        return render(request, 'admin/gamification/challenge_form.html', context)
    
    def add_view(self, request, form_url='', extra_context=None):
        """Redirect add view to custom create view"""
        return redirect('admin:gamification_challenge_create')
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Redirect change view to custom edit view"""
        return redirect('admin:gamification_challenge_edit', object_id=object_id)


@admin.register(UserChallengeProgress)
class UserChallengeProgressAdmin(ModelAdmin):
    list_display = ['user', 'challenge', 'status', 'completion_percentage', 'points_awarded', 'points_claimed', 'started_at', 'completed_at']
    list_filter = ['status', 'points_claimed', 'challenge__challenge_type', 'started_at']
    search_fields = ['user__username', 'user__email', 'challenge__name']
    readonly_fields = ['started_at', 'updated_at', 'points_awarded']
    date_hierarchy = 'started_at'
    raw_id_fields = ['user', 'challenge']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'challenge')

