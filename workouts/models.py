from django.db import models
from accounts.models import User


class WorkoutCategory(models.Model):
    """Categories for workouts"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'workout_categories'
        verbose_name = 'Workout Category'
        verbose_name_plural = 'Workout Categories'
    
    def __str__(self):
        return self.name


class Workout(models.Model):
    """Workout programs"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=255, blank=True, null=True)
    difficulty = models.CharField(max_length=20,
                                 choices=[
                                     ('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('advanced', 'Advanced'),
                                 ])
    category = models.ForeignKey(WorkoutCategory, on_delete=models.CASCADE, related_name='workouts')
    calories_burn = models.IntegerField(help_text="Estimated calories burned")
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    
    class Meta:
        db_table = 'workouts'
        verbose_name = 'Workout'
        verbose_name_plural = 'Workouts'
    
    def __str__(self):
        return self.title


class WorkoutRound(models.Model):
    """Rounds within a workout"""
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='rounds')
    name = models.CharField(max_length=100)
    round_order = models.IntegerField(help_text="Order of the round")
    
    class Meta:
        db_table = 'workout_rounds'
        verbose_name = 'Workout Round'
        verbose_name_plural = 'Workout Rounds'
        ordering = ['round_order']
    
    def __str__(self):
        return f"{self.workout.title} - {self.name}"


class Exercise(models.Model):
    """Exercises within a workout round"""
    round = models.ForeignKey(WorkoutRound, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=150)
    reps = models.IntegerField(blank=True, null=True, help_text="Number of repetitions")
    sets = models.IntegerField(blank=True, null=True, help_text="Number of sets")
    rest_seconds = models.IntegerField(blank=True, null=True, help_text="Rest time in seconds")
    video_url = models.URLField(max_length=255, blank=True, null=True)
    tips = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'exercises'
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
    
    def __str__(self):
        return self.name


class UserWorkoutProgress(models.Model):
    """Track user workout progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_progress')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    completed_rounds = models.JSONField(default=list, help_text="List of completed round IDs")
    date = models.DateField()
    calories_burned = models.FloatField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_workout_progress'
        verbose_name = 'User Workout Progress'
        verbose_name_plural = 'User Workout Progress'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.workout.title} - {self.date}"
