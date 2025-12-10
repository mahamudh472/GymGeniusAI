from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import User
from .tasks import generate_initial_workouts_task, generate_daily_workout_session_for_all_active_users
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def check_and_generate_workouts(sender, instance, created, **kwargs):
    """
    Signal handler that checks if user has completed their profile
    and triggers workout generation if all necessary data is available.
    
    This only runs once per user (tracked by initial_workouts_generated flag).
    """
    # Skip if workouts have already been generated
    if instance.initial_workouts_generated:
        return
    
    # Check if all necessary fields are filled
    required_fields = [
        instance.gender,
        instance.age,
        instance.weight_kg,
        instance.height_cm,
        instance.goal,
        instance.activity_level,
    ]
    
    # Check if all required fields have values
    if all(field is not None for field in required_fields):
        # All necessary data is available, trigger the celery task
        logger.info(f"Triggering workout generation for user {instance.email}")
        
        # Use apply_async to schedule the task
        generate_initial_workouts_task.apply_async(
            args=[str(instance.id)],
            countdown=5  # Wait 5 seconds before executing to allow transaction to complete
        )
    else:
        logger.debug(f"User {instance.email} profile incomplete, skipping workout generation")

@receiver(post_save, sender=User)
def generate_daily_workout(sender, instance, created, **kwargs):
    """
    Signal handler that generates a daily workout for the user
    whenever the user profile is updated.
    """
    from workouts.models import UserWorkout
    required_fields = [
        instance.gender,
        instance.age,
        instance.weight_kg,
        instance.height_cm,
        instance.goal,
        instance.activity_level,
    ]
    if not all(field is not None for field in required_fields):
        return

    if UserWorkout.objects.filter(user=instance, created_by_ai=True, created_at__date=timezone.now().date()).exists():
        return

    try:
        generate_daily_workout_session_for_all_active_users.apply_async(
            args=[str(instance.id)],
            countdown=10  # Wait 10 seconds before executing to allow transaction to complete
        )
        logger.info(f"Daily workout generated for user {instance.email}")
    except Exception as e:
        logger.error(f"Error generating daily workout for user {instance.email}: {e}")
