from django.contrib import admin
from .models import Community, Challenge, UserChallenge, Leaderboard
from unfold.admin import ModelAdmin

@admin.register(Community)
class CommunityAdmin(ModelAdmin):
    list_display = ['name', 'created_by']
    search_fields = ['name', 'description']


@admin.register(Challenge)
class ChallengeAdmin(ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'xp_reward', 'is_weekly', 'created_by']
    list_filter = ['is_weekly', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    ordering = ['-start_date']


@admin.register(UserChallenge)
class UserChallengeAdmin(ModelAdmin):
    list_display = ['user', 'challenge', 'progress', 'completed', 'xp_earned']
    list_filter = ['completed', 'challenge']
    search_fields = ['user__email', 'challenge__title']


@admin.register(Leaderboard)
class LeaderboardAdmin(ModelAdmin):
    list_display = ['rank', 'user', 'xp_points']
    ordering = ['rank']
    search_fields = ['user__email']
