from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Rank(models.Model):
    """
    Defines the ranking system (Bronze, Silver, Gold, etc.)
    """
    RANK_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
        ('MASTER', 'Master'),
    ]
    
    name = models.CharField(max_length=20, choices=RANK_CHOICES, unique=True)
    level = models.IntegerField(unique=True, help_text="Order of rank (1=lowest)")
    promotion_threshold = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Top X% get promoted weekly (e.g., 20.0 means top 20%)"
    )
    demotion_threshold = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Bottom X% get demoted weekly (e.g., 10.0 means bottom 10%)",
        default=0.0
    )
    min_points_required = models.IntegerField(
        default=0,
        help_text="Minimum points to maintain this rank"
    )
    icon = models.CharField(max_length=50, blank=True, null=True)
    color_code = models.CharField(max_length=7, default="#808080", help_text="Hex color code")
    
    class Meta:
        ordering = ['level']
        verbose_name = 'Rank'
        verbose_name_plural = 'Ranks'
    
    def __str__(self):
        return f"{self.get_name_display()} (Level {self.level})"


class ActivityType(models.Model):
    """
    Defines different activities that can earn points
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic use")
    points = models.IntegerField(help_text="Points awarded for this activity")
    description = models.TextField(blank=True, null=True)
    max_per_day = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Maximum times this activity can be counted per day (None for unlimited)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Activity Type'
        verbose_name_plural = 'Activity Types'
    
    def __str__(self):
        return f"{self.name} ({self.points} pts)"


class UserRank(models.Model):
    """
    Tracks user's current rank and rank history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_rank')
    current_rank = models.ForeignKey(Rank, on_delete=models.PROTECT, related_name='users')
    total_points = models.IntegerField(default=0)
    weekly_points = models.IntegerField(default=0)
    highest_rank_achieved = models.ForeignKey(
        Rank, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='highest_rank_users'
    )
    rank_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-weekly_points', '-total_points']
        verbose_name = 'User Rank'
        verbose_name_plural = 'User Ranks'
        indexes = [
            models.Index(fields=['-weekly_points', '-total_points']),
            models.Index(fields=['current_rank', '-weekly_points']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.current_rank.get_name_display()}"
    
    def reset_weekly_points(self):
        """Reset weekly points to 0"""
        self.weekly_points = 0
        self.save(update_fields=['weekly_points'])


class PointTransaction(models.Model):
    """
    Records all point transactions for transparency and history
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional data about the transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    week_start = models.DateField(help_text="Start of the week this transaction belongs to")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['week_start', 'user']),
            models.Index(fields=['activity_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.points} pts - {self.description}"


class WeeklyLeaderboard(models.Model):
    """
    Stores leaderboard snapshots for each week
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_rankings')
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name='weekly_leaderboards')
    week_start = models.DateField()
    week_end = models.DateField()
    position = models.IntegerField(help_text="Position within their rank/league")
    position_in_rank = models.IntegerField(help_text="Position among all users in same rank")
    total_users_in_rank = models.IntegerField(help_text="Total users in this rank this week")
    weekly_points = models.IntegerField()
    total_points = models.IntegerField()
    rank_changed = models.BooleanField(default=False)
    old_rank = models.ForeignKey(
        Rank, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='old_weekly_leaderboards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['week_start', 'rank__level', 'position_in_rank']
        verbose_name = 'Weekly Leaderboard'
        verbose_name_plural = 'Weekly Leaderboards'
        unique_together = ['user', 'week_start']
        indexes = [
            models.Index(fields=['week_start', 'rank', 'position_in_rank']),
            models.Index(fields=['user', '-week_start']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Week {self.week_start} - {self.rank.get_name_display()} #{self.position_in_rank}"


class RankHistory(models.Model):
    """
    Tracks rank changes over time
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rank_history')
    old_rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name='old_rank_history')
    new_rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name='new_rank_history')
    reason = models.CharField(max_length=100, help_text="Reason for rank change")
    weekly_points = models.IntegerField()
    position_in_old_rank = models.IntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)
    week_start = models.DateField()
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Rank History'
        verbose_name_plural = 'Rank Histories'
        indexes = [
            models.Index(fields=['user', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.old_rank.name} → {self.new_rank.name}"


class UserStreak(models.Model):
    """
    Tracks user daily check-in streaks
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_check_in = models.DateField(null=True, blank=True)
    total_check_ins = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'User Streak'
        verbose_name_plural = 'User Streaks'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} days streak"
    
    def check_in(self):
        """Process daily check-in and update streak"""
        today = timezone.now().date()
        
        if self.last_check_in == today:
            return False, "Already checked in today"
        
        if self.last_check_in == today - timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
        elif self.last_check_in is None or self.last_check_in < today - timedelta(days=1):
            # Streak broken or first check-in
            self.current_streak = 1
        
        self.last_check_in = today
        self.total_check_ins += 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()
        return True, f"Checked in! Current streak: {self.current_streak} days"


class Challenge(models.Model):
    """
    Defines challenges that users can participate in.
    A challenge is like a workout session but with time limits and rewards.
    """
    CHALLENGE_TYPE_CHOICES = [
        ('DAILY', 'Daily Challenge'),
        ('WEEKLY', 'Weekly Challenge'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=10, choices=CHALLENGE_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Reward points
    completion_points = models.IntegerField(help_text="Points awarded for completing the challenge")
    
    # Challenge duration
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Challenge content (workout reference)
    # This will be a JSON field containing exercises similar to UserWorkout
    exercises = models.JSONField(
        default=list,
        help_text=(
            "List of exercises with detailed information. Each exercise should include:\n"
            "- exercise_id (int, optional): ID from Exercise model to auto-populate details\n"
            "- name (str): Exercise name\n"
            "- sets (int): Number of sets\n"
            "- reps (int, optional): Reps per set\n"
            "- duration_seconds (int, optional): Duration for timed exercises\n"
            "- rest_time (int): Rest time between sets in seconds\n"
            "- notes (str, optional): Additional instructions\n"
            "If exercise_id is provided, description, video, muscle_group, difficulty, "
            "equipment_needed, calories_per_rep, and tips will be auto-populated from Exercise model."
        )
    )
    
    # Estimated metrics
    estimated_duration = models.IntegerField(
        blank=True, null=True,
        help_text="Estimated duration in minutes"
    )
    estimated_calories = models.IntegerField(
        blank=True, null=True,
        help_text="Estimated calories to burn"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='gamification_challenges_created',
        help_text="Admin or system that created this challenge"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
        indexes = [
            models.Index(fields=['challenge_type', 'is_active', 'start_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_challenge_type_display()})"
    
    def is_available(self):
        """Check if challenge is currently available"""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def time_remaining(self):
        """Get time remaining for the challenge"""
        if not self.is_available():
            return None
        now = timezone.now()
        remaining = self.end_date - now
        return remaining


class UserChallengeProgress(models.Model):
    """
    Tracks user's progress on a specific challenge.
    Similar to WorkoutProgress but for challenges.
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_progress')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    completed_exercises = models.JSONField(
        default=list,
        help_text="List of completed exercise indices from the challenge"
    )
    completion_percentage = models.FloatField(default=0.0)
    
    # Actual metrics
    actual_duration = models.IntegerField(
        blank=True, null=True,
        help_text="Actual duration in minutes"
    )
    actual_calories = models.FloatField(
        blank=True, null=True,
        help_text="Actual calories burned"
    )
    
    # Reward tracking
    points_awarded = models.IntegerField(default=0)
    points_claimed = models.BooleanField(default=False)
    
    # User feedback
    notes = models.TextField(blank=True, null=True)
    rating = models.IntegerField(
        blank=True, null=True,
        help_text="User rating (1-5)"
    )
    difficulty_rating = models.CharField(
        max_length=20, blank=True, null=True,
        choices=[
            ('too_easy', 'Too Easy'),
            ('just_right', 'Just Right'),
            ('too_hard', 'Too Hard'),
        ]
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'User Challenge Progress'
        verbose_name_plural = 'User Challenge Progress Records'
        unique_together = ['user', 'challenge']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['challenge', 'status']),
            models.Index(fields=['-completed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.name} ({self.get_status_display()})"
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage based on completed exercises"""
        total_exercises = len(self.challenge.exercises)
        if total_exercises == 0:
            return 0.0
        completed_count = len(self.completed_exercises)
        return (completed_count / total_exercises) * 100
    
    def check_and_award_points(self):
        """Check if challenge is completed and award points if not already done"""
        if self.status == 'COMPLETED' and not self.points_claimed:
            from .utils import award_points
            
            success, message, points = award_points(
                self.user,
                'CHALLENGE_COMPLETION',
                metadata={
                    'challenge_id': self.challenge.id,
                    'challenge_name': self.challenge.name,
                    'challenge_type': self.challenge.challenge_type
                },
                custom_points=self.challenge.completion_points
            )
            
            if success:
                self.points_awarded = points
                self.points_claimed = True
                self.save(update_fields=['points_awarded', 'points_claimed'])
                return True, message, points
            
            return False, message, 0
        
        return False, "Challenge not completed or points already claimed", 0
