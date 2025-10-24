from django.db import models
from accounts.models import User


class Community(models.Model):
    """User communities"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    
    class Meta:
        db_table = 'communities'
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'
    
    def __str__(self):
        return self.name


class Challenge(models.Model):
    """Fitness challenges"""
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    xp_reward = models.IntegerField(help_text="XP points reward")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    is_weekly = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'challenges'
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
    
    def __str__(self):
        return self.title


class UserChallenge(models.Model):
    """User participation in challenges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    progress = models.FloatField(default=0.0, help_text="Progress percentage")
    completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_challenges'
        verbose_name = 'User Challenge'
        verbose_name_plural = 'User Challenges'
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.email} - {self.challenge.title}"


class Leaderboard(models.Model):
    """User leaderboard rankings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard')
    xp_points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'leaderboard'
        verbose_name = 'Leaderboard Entry'
        verbose_name_plural = 'Leaderboard'
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.user.email} - Rank: {self.rank}"
