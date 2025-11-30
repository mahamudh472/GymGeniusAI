from .models import Exercise, ExerciseCategory, UserExercise, UserWorkout
from django.conf import settings
import json


def generate_workouts_for_user(workout_list=None, user=None):
    """
    Given a list of workout names and a user, return a list of Exercise objects
    that match the names in the workout_list.
    """

    for workout in workout_list:
        user_workout = UserWorkout.objects.create(
            user=user,
            name=workout['workout_name'],
            description=workout.get('description', ''),
            difficulty=workout.get('difficulty', 'beginner').lower(),
            estimated_duration=workout.get('estimated_duration', 0),
            estimated_calories=workout.get('estimated_calories', 0),
        )
        exercise_order = 1
        for exercise in workout['exercises']:
            try:
                exercise_obj = Exercise.objects.get(name=exercise['name'])
                user_exercise = UserExercise.objects.create(
                    user_workout=user_workout,
                    exercise=exercise_obj,
                    sets=exercise.get('sets', 3),
                    reps=exercise.get('reps', 12),
                    duration_seconds=exercise.get('duration_seconds', None),
                    rest_time=exercise.get('rest_time', 60),
                    order=exercise_order,
                    notes=exercise.get('notes', ''),
                )
                print(f"Created workout:{workout['workout_name']} exercise:{exercise['name']}, [{user_exercise.order}]")
                exercise_order += 1
            except Exercise.DoesNotExist:
                continue

