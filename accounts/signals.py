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
def generate_daily_workout(sender, instance, created, update_fields=None, **kwargs):
    """
    Signal handler that generates a daily workout AND updates calorie target
    for the user whenever the user profile is updated or they log in.
    """
    from workouts.models import UserWorkout

    # Avoid infinite recursion
    if update_fields and 'daily_calorie_target' in update_fields:
        return

    # Check for required profile fields
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

    # --- 1. Daily Workout Generation ---
    if not UserWorkout.objects.filter(user=instance, created_by_ai=True, created_at__date=timezone.now().date()).exists():
        try:
            generate_daily_workout_session_for_all_active_users.apply_async(
                args=[str(instance.id)],
                countdown=10
            )
            logger.info(f"Triggered daily workout generation for user {instance.email}")
        except Exception as e:
            logger.error(f"Error triggering workout generation for user {instance.email}: {e}")

    # --- 2. Daily Calorie Target Update ---
    # We want to trigger this if profile data OR last_login changed.
    # Since we can't easily track *what* changed without explicit update_fields in all calls,
    # and we definitely know we are NOT currently updating 'daily_calorie_target' (checked above),
    # we can safely trigger this. The task itself should be idempotent-ish (calculates based on current state).
    
    # We might want to avoid re-calculating on EVERY save if possible, but for now, 
    # ensures returning users get fresh data.
    from .tasks import update_daily_calorie_target_for_active_users
    try:
        update_daily_calorie_target_for_active_users.apply_async(
            args=[str(instance.id)],
            countdown=15
        )
        logger.info(f"Triggered calorie target update for user {instance.email}")
    except Exception as e:
        logger.error(f"Error triggering calorie update for user {instance.email}: {e}")
