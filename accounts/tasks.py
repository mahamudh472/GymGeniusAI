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


@shared_task
def generate_daily_workout_session_for_all_active_users(user_id=None):

    # users that logged in within the last 3 days
    from django.utils import timezone
    from datetime import timedelta
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            active_users = [user]
        except User.DoesNotExist:
            logger.error(f"User with id {user_id} does not exist")
            return
    else:
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=3)
        )

    for user in active_users:
        from ai_assistant.utils import generate_dataset_based_workout
        from gallery.models import UserGallery
        from workouts.models import Activity, UserWorkout
        from workouts.utils import generate_workouts_for_user
        
        if not all([user.gender, user.age, user.weight_kg, user.height_cm, user.goal, user.activity_level]):
            logger.info(f"Skipping user {user.email} due to incomplete profile data")
            continue

        if UserWorkout.objects.filter(user=user, created_by_ai=True, created_at__date=timezone.now().date()).exists():
            logger.info(f"Daily workout already generated for user {user.email} today")
            continue

        try:
            workout_logs = Activity.objects.filter(user=user).order_by('-created_at')[:5]

            workouts = generate_dataset_based_workout(
                gender=user.gender,
                age=user.age,
                weight_kg=user.weight_kg,
                height_cm=user.height_cm,
                goal=user.goal,
                activity_level=user.activity_level,
                username=user.profile_name,
                image_summary=UserGallery.objects.filter(user=user).first().ai_summary if UserGallery.objects.filter(user=user).exists() else "",
                workout_logs=workout_logs
            )
            print(workouts)
            generate_workouts_for_user(workout_list=[workouts], user=user)
            logger.info(f"Generated daily workout session for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to generate daily workout for user {user.email}: {str(e)}")


@shared_task
def update_daily_calorie_target_for_active_users(user_id=None):
    from django.utils import timezone
    from datetime import timedelta
    from ai_assistant.utils import get_target_calories, update_daily_calorie_target
    from gallery.models import UserGallery

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            active_users = [user]
        except User.DoesNotExist:
            logger.error(f"User with id {user_id} does not exist")
            return
    else:
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=3)
        )
    
    for user in active_users:
        if not all([user.gender, user.age, user.weight_kg, user.height_cm, user.goal, user.activity_level]):
            logger.info(f"Skipping calorie update for user {user.email} due to incomplete profile data")
            continue
            
        try:
            gallery = UserGallery.objects.filter(user=user).first()
            image_summary = gallery.ai_summary if gallery else ""
            
            result = get_target_calories(
                gender=user.gender,
                age=user.age,
                weight_kg=user.weight_kg,
                height_cm=user.height_cm,
                goal=user.goal,
                activity_level=user.activity_level,
                username=user.profile_name,
                image_summary=image_summary
            )
            
            if 'error' in result:
                logger.error(f"Error getting calorie target for {user.email}: {result['error']}")
                continue
                
            monthly_calories = result.get('target_calories_per_Month')
            if not monthly_calories:
                logger.error(f"No target_calories_per_Month returned for {user.email}")
                continue
            
            # Convert monthly to daily (approx 30 days)
            daily_calories = int(monthly_calories / 30)
            
            if update_daily_calorie_target(user, daily_calories):
                logger.info(f"Updated daily calorie target for user {user.email}: {daily_calories}")
            else:
                 logger.error(f"Failed to update daily calorie target for user {user.email}")

        except Exception as e:
            logger.error(f"Failed to update calorie target for user {user.email}: {str(e)}")

