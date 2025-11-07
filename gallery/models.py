from django.db import models
from accounts.models import User


class UserGallery(models.Model):
    """User progress photos and gallery"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='user_gallery/')
    image_type = models.CharField(max_length=20,
                                  choices=[
                                      ('front', 'Front'),
                                      ('side', 'Side'),
                                      ('back', 'Back'),
                                  ])
    ai_detected = models.BooleanField(default=False, help_text="AI body composition analysis")
    ai_summary = models.TextField(blank=True, null=True,
                                  help_text="AI-generated summary of body composition")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_gallery'
        verbose_name = 'User Gallery Image'
        verbose_name_plural = 'User Gallery Images'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.image_type} - {self.uploaded_at.strftime('%Y-%m-%d')}"
