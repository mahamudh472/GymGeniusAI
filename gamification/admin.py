from django.contrib import admin
from .models import (
    Rank, ActivityType, UserRank, PointTransaction,
    WeeklyLeaderboard, RankHistory, UserStreak
)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'promotion_threshold', 'demotion_threshold', 'min_points_required', 'color_code']
    list_filter = ['level']
    search_fields = ['name']
    ordering = ['level']


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'points', 'max_per_day', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserRank)
class UserRankAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_rank', 'total_points', 'weekly_points', 'rank_updated_at']
    list_filter = ['current_rank', 'rank_updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'rank_updated_at']
    ordering = ['-weekly_points', '-total_points']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'current_rank', 'highest_rank_achieved')


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'points', 'description', 'created_at', 'week_start']
    list_filter = ['activity_type', 'created_at', 'week_start']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'activity_type')


@admin.register(WeeklyLeaderboard)
class WeeklyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'rank', 'week_start', 'position_in_rank', 'weekly_points', 'rank_changed']
    list_filter = ['rank', 'week_start', 'rank_changed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'week_start'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'rank', 'old_rank')


@admin.register(RankHistory)
class RankHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'old_rank', 'new_rank', 'reason', 'weekly_points', 'changed_at']
    list_filter = ['old_rank', 'new_rank', 'changed_at']
    search_fields = ['user__username', 'user__email', 'reason']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'old_rank', 'new_rank')


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_check_in', 'total_check_ins']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_check_in']
    ordering = ['-current_streak']
