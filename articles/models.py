from django.db import models
from accounts.models import User


class Article(models.Model):
    """Articles and fitness tips"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    media_url = models.URLField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100,
                               choices=[
                                   ('fitness', 'Fitness'),
                                   ('nutrition', 'Nutrition'),
                                   ('wellness', 'Wellness'),
                                   ('motivation', 'Motivation'),
                                   ('tips', 'Tips'),
                               ])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'articles'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class WorkoutVideo(models.Model):
    video_url = models.URLField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_videos'
        verbose_name = 'Workout Video'
        verbose_name_plural = 'Workout Videos'
    
    def __str__(self):
        return f"{self.title} ({self.duration_minutes} mins)"