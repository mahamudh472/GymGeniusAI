from rest_framework import serializers
from .models import (
    Rank, UserRank, PointTransaction, ActivityType,
    WeeklyLeaderboard, RankHistory, UserStreak, Challenge, UserChallengeProgress
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
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRank
        fields = [
            'id', 'username', 'current_rank', 'total_points', 'weekly_points',
            'highest_rank_achieved', 'rank_updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'current_rank', 'total_points', 
                           'weekly_points', 'highest_rank_achieved', 
                           'rank_updated_at', 'created_at']
    def get_username(self, obj):
        return obj.user.profile_name


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointTransaction model"""
    activity_name = serializers.CharField(source='activity_type.name', read_only=True)
    username = serializers.CharField(source='user.profile_name', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'username', 'activity_type', 'activity_name', 'points',
            'description', 'metadata', 'created_at', 'week_start'
        ]
        read_only_fields = ['id', 'username', 'activity_name', 'created_at']


class WeeklyLeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for WeeklyLeaderboard model"""
    username = serializers.CharField(source='user.profile_name', read_only=True)
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
    username = serializers.CharField(source='user.profile_name', read_only=True)
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
    username = serializers.CharField(source='user.profile_name')
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


class ChallengeExerciseSerializer(serializers.Serializer):
    """Serializer for enriched challenge exercises with full exercise details"""
    exercise_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    video = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    muscle_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    equipment_needed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    calories_per_rep = serializers.FloatField(required=False, allow_null=True)
    sets = serializers.IntegerField()
    reps = serializers.IntegerField(required=False, allow_null=True)
    duration_seconds = serializers.IntegerField(required=False, allow_null=True)
    rest_time = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tips = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for Challenge model"""
    challenge_type_display = serializers.CharField(source='get_challenge_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    is_available = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'name', 'description', 'challenge_type', 'challenge_type_display',
            'difficulty', 'difficulty_display', 'completion_points', 'start_date',
            'end_date', 'exercises', 'estimated_duration', 'estimated_calories',
            'is_active', 'is_available', 'time_remaining_seconds', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_available(self, obj):
        return obj.is_available()
    
    def get_time_remaining_seconds(self, obj):
        remaining = obj.time_remaining()
        if remaining:
            return remaining.total_seconds()
        return None
    
    def get_exercises(self, obj):
        """Enrich exercise data with full Exercise model details"""
        from apps.workouts.models import Exercise
        
        enriched_exercises = []
        for exercise_data in obj.exercises:
            enriched = exercise_data.copy()
            
            # If exercise_id is present, fetch full exercise details
            exercise_id = exercise_data.get('exercise_id')
            if exercise_id:
                try:
                    exercise = Exercise.objects.get(id=exercise_id)
                    enriched['name'] = exercise.name
                    enriched['description'] = exercise.description
                    enriched['muscle_group'] = exercise.muscle_group
                    enriched['difficulty'] = exercise.difficulty
                    enriched['duration_seconds'] = exercise.default_duration_seconds
                    enriched['equipment_needed'] = exercise.equipment_needed
                    enriched['calories_per_rep'] = exercise.calories_per_rep
                    enriched['tips'] = exercise.tips
                    
                    # Build absolute video URL if video exists
                    request = self.context.get('request')
                    video_url = None
                    
                    # 1. Try to get coach-specific video if request and user exist
                    if request and hasattr(request, 'user') and request.user.is_authenticated and getattr(request.user, 'coach_type', None):
                        coach_video = exercise.videos.filter(coach=request.user.coach_type).first()
                        if coach_video and coach_video.video_file and hasattr(coach_video.video_file, 'url'):
                            video_url = request.build_absolute_uri(coach_video.video_file.url)
                    
                    # 2. Fallback to default exercise video if no coach video found
                    if not video_url and exercise.video and hasattr(exercise.video, 'url'):
                        if request:
                            video_url = request.build_absolute_uri(exercise.video.url)
                        else:
                            video_url = exercise.video.url
                    
                    enriched['video'] = video_url
                except Exercise.DoesNotExist:
                    # If exercise not found, keep original data
                    pass
            
            enriched_exercises.append(enriched)
        
        return enriched_exercises


class UserChallengeProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserChallengeProgress model"""
    challenge = ChallengeSerializer(read_only=True)
    challenge_id = serializers.IntegerField(write_only=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserChallengeProgress
        fields = [
            'id', 'username', 'challenge', 'challenge_id', 'status', 'status_display',
            'completed_exercises', 'completion_percentage', 'actual_duration',
            'actual_calories', 'points_awarded', 'points_claimed', 'notes',
            'rating', 'difficulty_rating', 'started_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'points_awarded', 'points_claimed',
            'started_at', 'completed_at', 'updated_at'
        ]


class StartChallengeSerializer(serializers.Serializer):
    """Serializer for starting a challenge"""
    challenge_id = serializers.IntegerField()


class CompleteChallengeExerciseSerializer(serializers.Serializer):
    """Serializer for completing an exercise in a challenge"""
    challenge_id = serializers.IntegerField()
    exercise_index = serializers.IntegerField(min_value=0)
    actual_sets = serializers.IntegerField(required=False, allow_null=True)
    actual_reps = serializers.IntegerField(required=False, allow_null=True)
    actual_duration = serializers.IntegerField(required=False, allow_null=True, help_text="Duration in seconds")
    notes = serializers.CharField(required=False, allow_blank=True)


class ClaimChallengeRewardSerializer(serializers.Serializer):
    """Serializer for claiming challenge reward"""
    challenge_progress_id = serializers.IntegerField()
