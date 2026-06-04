from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserGallery
from .tasks import analyze_gallery_image
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserGallery)
def analyze_image_ai(sender, instance, created, **kwargs):
    """Trigger AI analysis on new gallery image upload"""
    if created and not instance.ai_detected:
        logger.info(f"New gallery image created with ID: {instance.id}. Triggering AI analysis...")
        # Trigger the Celery task to analyze the image in the background
        analyze_gallery_image.delay(instance.id)
        logger.info(f"AI analysis task queued for gallery image ID: {instance.id}")