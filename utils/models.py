from django.db import models
from accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    """User notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('reminder', 'Reminders'),
        ('system', 'System Alerts'),
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    
    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} favorited {self.content_object}"


# from django.contrib.contenttypes.models import ContentType
# from myapp.models import Favorite, Workout, Article, Video

# # Example: user favorites a workout
# workout = Workout.objects.get(id=1)
# Favorite.objects.create(user=request.user, content_object=workout)

# # Get all user favorites
# user_favorites = request.user.favorites.all()

# # Get only favorite workouts
# from django.contrib.contenttypes.models import ContentType
# workout_type = ContentType.objects.get_for_model(Workout)
# favorite_workouts = Favorite.objects.filter(user=request.user, content_type=workout_type)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    type = models.CharField(max_length=100, choices=[('general', 'General'), ('account', 'Account'), ('service', 'Service')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class ContactOption(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='contact_icons/')
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name