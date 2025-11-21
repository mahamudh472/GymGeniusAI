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
