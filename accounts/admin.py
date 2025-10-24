from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, SubscriptionPlan, UserSubscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_verified', 'gender', 'goal', 'joined_at']
    list_filter = ['is_verified', 'gender', 'goal', 'activity_level', 'is_staff']
    search_fields = ['email', 'username', 'phone_number']
    ordering = ['-joined_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('phone_number', 'is_verified', 'gender', 'age', 'height_cm', 'weight_kg')
        }),
        ('Fitness Goals', {
            'fields': ('goal', 'activity_level', 'coach_type', 'subscription_id')
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'purpose', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used']
    search_fields = ['user__email', 'code']
    ordering = ['-created_at']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'payment_status']
    list_filter = ['is_active', 'payment_status']
    search_fields = ['user__email', 'transaction_id']
    ordering = ['-start_date']
