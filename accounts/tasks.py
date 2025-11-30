from celery import shared_task
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def generate_initial_workouts_task(self, user_id):
    """
    Celery task to generate initial workouts for a user.
    This task is triggered when a user completes their profile with all necessary data.
    It runs only once per user.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Check if workouts have already been generated
        if user.initial_workouts_generated:
            logger.info(f"Workouts already generated for user {user.email}")
            return {
                'status': 'skipped',
                'message': 'Workouts already generated for this user'
            }
        
        # Import here to avoid circular imports
        from ai_assistant.utils import generate_multi_level_workouts
        from workouts.utils import generate_workouts_for_user
        
        # Generate workouts using AI
        response = generate_multi_level_workouts(
            gender=user.gender,
            age=user.age,
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            goal=user.goal,
            activity_level=user.activity_level,
            username=user.profile_name
        )
        
        workouts = response.get('workout_levels', [])
        
        if not workouts:
            raise ValueError("No workouts were generated")
        
        # Create workout records for the user
        generate_workouts_for_user(workout_list=workouts, user=user)
        
        # Mark as completed
        user.initial_workouts_generated = True
        user.save(update_fields=['initial_workouts_generated'])
        
        logger.info(f"Successfully generated {len(workouts)} workouts for user {user.email}")
        
        return {
            'status': 'success',
            'message': f'Generated {len(workouts)} workouts successfully',
            'workout_count': len(workouts)
        }
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return {
            'status': 'error',
            'message': 'User not found'
        }
    
    except Exception as e:
        logger.error(f"Error generating workouts for user {user_id}: {str(e)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
