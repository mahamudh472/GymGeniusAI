# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import UserUploadedMeal
# from .tasks import analyze_uploaded_meal
# import logging

# logger = logging.getLogger(__name__)
# @receiver(post_save, sender=UserUploadedMeal)
# def trigger_ai_analysis(sender, instance, created, **kwargs):
#     """Trigger AI analysis on new user uploaded meal image"""
#     if created and not instance.ai_analysis:
#         logger.info(f"New user uploaded meal created with ID: {instance.id}. Triggering AI analysis...")
#         analyze_uploaded_meal.delay(instance.id)

