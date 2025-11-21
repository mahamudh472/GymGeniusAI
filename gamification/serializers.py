from rest_framework import serializers
from .models import (
    Rank, UserRank, PointTransaction, ActivityType,
    WeeklyLeaderboard, RankHistory, UserStreak
)
from django.contrib.auth import get_user_model

User = get_user_model()


class RankSerializer(serializers.ModelSerializer):
    """Serializer for Rank model"""
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Rank
        fields = [
            'id', 'name', 'name_display', 'level', 'promotion_threshold',
            'demotion_threshold', 'min_points_required', 'icon', 'color_code'
        ]
        read_only_fields = ['id']


class ActivityTypeSerializer(serializers.ModelSerializer):
    """Serializer for ActivityType model"""
    
    class Meta:
        model = ActivityType
        fields = [
            'id', 'name', 'code', 'points', 'description',
            'max_per_day', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserStreakSerializer(serializers.ModelSerializer):
    """Serializer for UserStreak model"""
    
    class Meta:
        model = UserStreak
        fields = [
            'current_streak', 'longest_streak', 'last_check_in', 'total_check_ins'
        ]
        read_only_fields = ['current_streak', 'longest_streak', 'last_check_in', 'total_check_ins']


class UserRankSerializer(serializers.ModelSerializer):
    """Serializer for UserRank model"""
    current_rank = RankSerializer(read_only=True)
    highest_rank_achieved = RankSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserRank
        fields = [
            'id', 'username', 'current_rank', 'total_points', 'weekly_points',
            'highest_rank_achieved', 'rank_updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'current_rank', 'total_points', 
                           'weekly_points', 'highest_rank_achieved', 
                           'rank_updated_at', 'created_at']


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointTransaction model"""
    activity_name = serializers.CharField(source='activity_type.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'username', 'activity_type', 'activity_name', 'points',
            'description', 'metadata', 'created_at', 'week_start'
        ]
        read_only_fields = ['id', 'username', 'activity_name', 'created_at']


class WeeklyLeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for WeeklyLeaderboard model"""
    username = serializers.CharField(source='user.username', read_only=True)
    rank_name = serializers.CharField(source='rank.get_name_display', read_only=True)
    rank_color = serializers.CharField(source='rank.color_code', read_only=True)
    old_rank_name = serializers.CharField(source='old_rank.get_name_display', read_only=True)
    
    class Meta:
        model = WeeklyLeaderboard
        fields = [
            'id', 'username', 'rank_name', 'rank_color', 'week_start', 'week_end',
            'position', 'position_in_rank', 'total_users_in_rank', 'weekly_points',
            'total_points', 'rank_changed', 'old_rank_name', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'rank_name', 'rank_color', 
                           'old_rank_name', 'created_at']


class RankHistorySerializer(serializers.ModelSerializer):
    """Serializer for RankHistory model"""
    username = serializers.CharField(source='user.username', read_only=True)
    old_rank_name = serializers.CharField(source='old_rank.get_name_display', read_only=True)
    new_rank_name = serializers.CharField(source='new_rank.get_name_display', read_only=True)
    
    class Meta:
        model = RankHistory
        fields = [
            'id', 'username', 'old_rank_name', 'new_rank_name', 'reason',
            'weekly_points', 'position_in_old_rank', 'changed_at', 'week_start'
        ]
        read_only_fields = ['id', 'username', 'old_rank_name', 'new_rank_name', 'changed_at']


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entries"""
    position = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    weekly_points = serializers.IntegerField()
    total_points = serializers.IntegerField()
    is_current_user = serializers.BooleanField()


class LeaderboardResponseSerializer(serializers.Serializer):
    """Serializer for complete leaderboard response"""
    rank = serializers.CharField()
    rank_level = serializers.IntegerField()
    rank_color = serializers.CharField()
    user_position = serializers.IntegerField()
    total_users_in_rank = serializers.IntegerField()
    week_start = serializers.CharField()
    leaderboard = LeaderboardEntrySerializer(many=True)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user stats"""
    user = serializers.DictField()
    rank = serializers.DictField()
    points = serializers.DictField()
    position = serializers.DictField()
    streak = serializers.DictField()
    highest_rank = serializers.DictField()
    recent_transactions = serializers.ListField()
    rank_history = serializers.ListField()


class AwardPointsSerializer(serializers.Serializer):
    """Serializer for awarding points"""
    activity_code = serializers.CharField(max_length=50)
    metadata = serializers.JSONField(required=False, default=dict)
    custom_points = serializers.IntegerField(required=False, allow_null=True)


class CheckInResponseSerializer(serializers.Serializer):
    """Serializer for check-in response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    points_awarded = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    total_check_ins = serializers.IntegerField()
