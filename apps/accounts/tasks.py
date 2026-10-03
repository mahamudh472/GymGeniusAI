from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def _is_admin_account(user):
    return user.is_staff or user.is_superuser


def _daily_workout_from_response(response):
    """Validate the AI response before attempting to create workout records."""
    if not isinstance(response, dict):
        raise ValueError('AI returned a non-object workout response.')
    if response.get('error'):
        raise ValueError(f"AI workout generation failed: {response['error']}")
    if 'workout_name' not in response:
        raise ValueError(
            'AI response is missing workout_name. '
            f"Received keys: {', '.join(sorted(response.keys())) or 'none'}"
        )
    if not isinstance(response.get('exercises'), list):
        raise ValueError('AI response is missing a valid exercises list.')
    return response


def _update_job(job_id, **fields):
    """Update a job without letting a monitoring failure stop workout generation."""
    if not job_id:
        return None
    from .models import WorkoutGenerationJob
    WorkoutGenerationJob.objects.filter(pk=job_id).update(**fields)
    return WorkoutGenerationJob.objects.filter(pk=job_id).first()


@shared_task(bind=True, max_retries=3)
def generate_initial_workouts_task(self, user_id, job_id=None):
    """
    Celery task to generate initial workouts for a user.
    This task is triggered when a user completes their profile with all necessary data.
    It runs only once per user.
    """
    try:
        from .models import WorkoutGenerationJob
        if job_id and WorkoutGenerationJob.objects.filter(
            pk=job_id, status=WorkoutGenerationJob.Status.REVOKED
        ).exists():
            return {'status': 'revoked', 'message': 'Job was revoked before execution'}
        job = _update_job(
            job_id,
            status='started',
            started_at=timezone.now(),
            attempts=self.request.retries + 1,
            error='',
        )
        user = User.objects.get(id=user_id)
        if _is_admin_account(user):
            result = {
                'status': 'skipped',
                'message': 'Workout generation is disabled for admin accounts',
            }
            _update_job(job_id, status='success', result=result, completed_at=timezone.now())
            return result
        
        # Check if workouts have already been generated
        if user.initial_workouts_generated:
            logger.info(f"Workouts already generated for user {user.email}")
            result = {
                'status': 'skipped',
                'message': 'Workouts already generated for this user'
            }
            _update_job(job_id, status='success', result=result, completed_at=timezone.now())
            return result
        
        # Import here to avoid circular imports
        from apps.ai_assistant.utils import generate_multi_level_workouts
        from apps.workouts.utils import generate_workouts_for_user
        
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
        
        # Create workout records for the user with initial origin
        generate_workouts_for_user(workout_list=workouts, user=user, origin='initial')
        
        # Mark as completed
        user.initial_workouts_generated = True
        user.save(update_fields=['initial_workouts_generated'])
        
        logger.info(f"Successfully generated {len(workouts)} workouts for user {user.email}")
        
        result = {
            'status': 'success',
            'message': f'Generated {len(workouts)} workouts successfully',
            'workout_count': len(workouts)
        }
        _update_job(job_id, status='success', result=result, completed_at=timezone.now())
        return result
    except Exception as e:
        logger.error(f"Error generating initial workouts for user {user_id}: {str(e)}")
        if self.request.retries >= self.max_retries:
            _update_job(job_id, status='failure', error=str(e), completed_at=timezone.now())
            raise
        _update_job(job_id, status='retrying', error=str(e))
        raise self.retry(exc=e, countdown=60)


@shared_task
def generate_daily_workout_session_for_all_active_users(user_id=None, job_id=None):
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
            last_login__gte=timezone.now() - timedelta(days=3),
            is_staff=False,
            is_superuser=False,
        )

    from .models import WorkoutGenerationJob
    if job_id and WorkoutGenerationJob.objects.filter(
        pk=job_id, status=WorkoutGenerationJob.Status.REVOKED
    ).exists():
        return {'status': 'revoked', 'message': 'Job was revoked before execution'}
    _update_job(job_id, status='started', started_at=timezone.now(), attempts=1, error='')
    generated_count = 0
    errors = []
    for user in active_users:
        if _is_admin_account(user):
            continue
        from apps.ai_assistant.utils import generate_dataset_based_workout
        from apps.gallery.models import UserGallery
        from apps.workouts.models import Activity, UserWorkout
        from apps.workouts.utils import generate_workouts_for_user
        
        if not all([user.gender, user.age, user.weight_kg, user.height_cm, user.goal, user.activity_level]):
            logger.info(f"Skipping user {user.email} due to incomplete profile data")
            continue

        if UserWorkout.objects.filter(user=user, origin='daily', created_at__date=timezone.now().date()).exists():
            logger.info(f"Daily workout already generated for user {user.email} today")
            continue

        try:
            workout_logs = list(
                Activity.objects.filter(user=user)
                .order_by('-created_at')
                .values('name', 'duration', 'calories')[:5]
            )

            workout = _daily_workout_from_response(generate_dataset_based_workout(
                gender=user.gender,
                age=user.age,
                weight_kg=user.weight_kg,
                height_cm=user.height_cm,
                goal=user.goal,
                activity_level=user.activity_level,
                username=user.profile_name,
                image_summary=UserGallery.objects.filter(user=user).first().ai_summary if UserGallery.objects.filter(user=user).exists() else "",
                workout_logs=workout_logs
            ))
            generate_workouts_for_user(workout_list=[workout], user=user, origin='daily')
            generated_count += 1
            logger.info(f"Generated daily workout session for user {user.email}")
        except Exception as e:
            errors.append(str(e))
            logger.exception("Failed to generate daily workout for user %s", user.email)

    result = {
        'status': 'failure' if errors else 'success',
        'workout_count': generated_count,
        'errors': errors,
    }
    if job_id:
        _update_job(
            job_id,
            status='failure' if errors else 'success',
            result=result,
            error='\n'.join(errors),
            completed_at=timezone.now(),
        )
    return result


def queue_workout_generation(user, job_type, countdown=0, job=None):
    """Create an admin-visible job and submit its matching Celery task."""
    from .models import WorkoutGenerationJob

    if _is_admin_account(user):
        raise ValueError('Workout generation is disabled for admin accounts.')

    if job is None:
        job = WorkoutGenerationJob.objects.create(user=user, job_type=job_type)
    task = (
        generate_initial_workouts_task
        if job_type == WorkoutGenerationJob.JobType.INITIAL
        else generate_daily_workout_session_for_all_active_users
    )
    result = task.apply_async(args=[str(user.id), job.pk], countdown=countdown)
    job.celery_task_id = result.id
    job.save(update_fields=['celery_task_id'])
    return job


@shared_task
def update_daily_calorie_target_for_active_users(user_id=None):
    from django.utils import timezone
    from datetime import timedelta
    from apps.ai_assistant.utils import get_target_calories, update_daily_calorie_target
    from apps.gallery.models import UserGallery

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
