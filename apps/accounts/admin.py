from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, SubscriptionPlan, UserSubscription, WorkoutGenerationJob
from unfold.admin import ModelAdmin
from celery import current_app
from django.contrib import messages
from django.utils import timezone
from .tasks import queue_workout_generation

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'is_verified', 'gender', 'goal', 'joined_at']
    list_filter = ['is_verified', 'gender', 'goal', 'activity_level', 'is_staff']
    search_fields = ['email', 'phone_number']
    ordering = ['-joined_at']
    list_per_page = 50
    
    # Override fieldsets to remove date_joined
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),  # removed date_joined
        ('Profile Information', {
            'fields': ('full_name', 'phone_number', 'is_verified', 'gender', 'age', 'height_cm', 'weight_kg', 'avatar')
        }),
        ('Fitness Goals', {
            'fields': ('goal', 'activity_level', 'coach_type', 'subscription_id')
        }),
    )

    # Optional: if you use add_fieldsets for creating users in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number'),
        }),
    )

    actions = ['queue_initial_workouts', 'queue_daily_workout']

    @admin.action(description='Queue initial AI workout generation')
    def queue_initial_workouts(self, request, queryset):
        count = 0
        for user in queryset:
            if user.is_profile_completed and not (user.is_staff or user.is_superuser):
                queue_workout_generation(user, WorkoutGenerationJob.JobType.INITIAL)
                count += 1
        self.message_user(request, f'Queued {count} initial workout job(s).', messages.SUCCESS)

    @admin.action(description='Queue daily AI workout generation')
    def queue_daily_workout(self, request, queryset):
        count = 0
        for user in queryset:
            if user.is_profile_completed and not (user.is_staff or user.is_superuser):
                queue_workout_generation(user, WorkoutGenerationJob.JobType.DAILY)
                count += 1
        self.message_user(request, f'Queued {count} daily workout job(s).', messages.SUCCESS)


@admin.register(WorkoutGenerationJob)
class WorkoutGenerationJobAdmin(ModelAdmin):
    list_display = ['id', 'user', 'job_type', 'status', 'attempts', 'celery_task_id', 'created_at', 'started_at', 'completed_at']
    list_filter = ['job_type', 'status', 'created_at']
    search_fields = ['user__email', 'celery_task_id']
    ordering = ['-created_at']
    list_select_related = ['user']
    raw_id_fields = ['user']
    readonly_fields = [field.name for field in WorkoutGenerationJob._meta.fields]
    actions = ['retry_jobs', 'revoke_jobs']

    @admin.action(description='Retry selected jobs')
    def retry_jobs(self, request, queryset):
        jobs = list(queryset.filter(status__in=['failure', 'revoked']))
        for job in jobs:
            job.status = WorkoutGenerationJob.Status.PENDING
            job.error = ''
            job.result = {}
            job.started_at = None
            job.completed_at = None
            job.celery_task_id = ''
            job.save(update_fields=['status', 'error', 'result', 'started_at', 'completed_at', 'celery_task_id'])
            queue_workout_generation(job.user, job.job_type, job=job)
        self.message_user(request, f'Requeued {len(jobs)} job(s).', messages.SUCCESS)

    @admin.action(description='Revoke selected pending or running jobs')
    def revoke_jobs(self, request, queryset):
        jobs = queryset.exclude(status__in=['success', 'failure', 'revoked'])
        count = 0
        for job in jobs:
            if job.celery_task_id:
                current_app.control.revoke(job.celery_task_id, terminate=False)
            job.status = WorkoutGenerationJob.Status.REVOKED
            job.completed_at = timezone.now()
            job.save(update_fields=['status', 'completed_at'])
            count += 1
        self.message_user(request, f'Revoked {count} job(s).', messages.SUCCESS)

    def has_add_permission(self, request):
        return False


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_per_page = 50


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'payment_status']
    list_filter = ['is_active', 'payment_status']
    search_fields = ['user__email', 'transaction_id']
    ordering = ['-start_date']
    raw_id_fields = ['user', 'plan']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')
