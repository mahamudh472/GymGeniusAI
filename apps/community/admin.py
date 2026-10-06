from django.contrib import admin
from .models import Community, Challenge, UserChallenge, Leaderboard, ForumPostReport, ForumCommentReport, UserBlock
from unfold.admin import ModelAdmin

@admin.register(Community)
class CommunityAdmin(ModelAdmin):
    list_display = ['name', 'created_by']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Challenge)
class ChallengeAdmin(ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'xp_reward', 'is_weekly', 'created_by']
    list_filter = ['is_weekly', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    ordering = ['-start_date']
    raw_id_fields = ['created_by']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(UserChallenge)
class UserChallengeAdmin(ModelAdmin):
    list_display = ['user', 'challenge', 'progress', 'completed', 'xp_earned']
    list_filter = ['completed', 'challenge']
    search_fields = ['user__email', 'challenge__title']
    raw_id_fields = ['user', 'challenge']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'challenge')


@admin.register(Leaderboard)
class LeaderboardAdmin(ModelAdmin):
    list_display = ['rank', 'user', 'xp_points']
    ordering = ['rank']
    search_fields = ['user__email']
    raw_id_fields = ['user']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ForumPostReport)
class ForumPostReportAdmin(ModelAdmin):
    list_display = ['post', 'reported_by', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reported_by__email', 'description']
    raw_id_fields = ['post', 'reported_by']
    list_per_page = 50
    list_editable = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'reported_by')


@admin.register(ForumCommentReport)
class ForumCommentReportAdmin(ModelAdmin):
    list_display = ['comment', 'reported_by', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reported_by__email', 'description']
    raw_id_fields = ['comment', 'reported_by']
    list_per_page = 50
    list_editable = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comment', 'reported_by')


@admin.register(UserBlock)
class UserBlockAdmin(ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    search_fields = ['blocker__email', 'blocked__email']
    raw_id_fields = ['blocker', 'blocked']
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blocker', 'blocked')

