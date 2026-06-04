from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, SubscriptionPlan, UserSubscription
from unfold.admin import ModelAdmin

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
