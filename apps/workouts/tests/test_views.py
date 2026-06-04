from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.accounts.models import User
from apps.workouts.models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity,
    CustomRoutine, CustomRoutineExercise, CustomRoutineExerciseCompletion
)

class WorkoutsViewsTests(APITestCase):
    def setUp(self):
        # Create active verified user
        self.user = User.objects.create_user(
            email="workoutuser@example.com",
            password="password123",
            full_name="Workout User",
            is_verified=True
        )
        
        # Create Exercise Category
        self.category = ExerciseCategory.objects.create(
            name="Cardio",
            description="Cardiovascular exercises"
        )
        
        # Create Exercise
        self.exercise = Exercise.objects.create(
            name="Treadmill Run",
            description="Run on treadmill",
            muscle_group="Legs",
            category=self.category,
            difficulty="beginner",
            default_sets=3,
            default_reps=10,
            default_rest_time=60,
            calories_per_rep=0.8
        )
        
        # Create UserWorkout
        self.workout = UserWorkout.objects.create(
            user=self.user,
            name="Morning Cardio Blast",
            description="Wake up cardio",
            difficulty="beginner",
            estimated_duration=30,
            estimated_calories=200
        )
        
        # Add Exercise to Workout
        self.user_exercise = UserExercise.objects.create(
            user_workout=self.workout,
            exercise=self.exercise,
            sets=3,
            reps=10,
            order=1
        )
        
        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "workoutuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # URLs
        self.workout_list_url = reverse('workouts:user-workouts')
        self.workout_detail_url = reverse('workouts:user-workout-detail', kwargs={'pk': self.workout.id})
        self.track_progress_url = reverse('workouts:track-workout-progress')
        self.activity_list_url = reverse('workouts:activity-list')
        self.daily_progress_url = reverse('workouts:daily-progress')
        self.recommendation_url = reverse('workouts:workout-recommendation')
        self.exercise_list_url = reverse('workouts:exercise-list')
        self.custom_routine_url = reverse('workouts:custom-routine')
        self.toggle_exercise_url = reverse('workouts:toggle-custom-routine-exercise')
        self.custom_routine_exercises_url = reverse('workouts:custom-routine-exercises')
        self.complete_custom_exercise_url = reverse('workouts:complete-custom-routine-exercise')
        self.completion_history_url = reverse('workouts:custom-routine-completion-history')

    def test_list_workouts(self):
        response = self.client.get(self.workout_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Morning Cardio Blast")

    def test_workout_detail(self):
        response = self.client.get(self.workout_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Morning Cardio Blast")

    def test_track_progress_post_and_get(self):
        payload = {
            "user_workout_id": self.workout.id,
            "user_exercise_id": self.user_exercise.id,
            "actual_sets": 3,
            "actual_reps": 10,
            "notes": "Felt good"
        }
        response = self.client.post(self.track_progress_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['all_completed'])
        
        # Test Get Workout Progress
        response_get = self.client.get(f"{self.track_progress_url}?user_workout_id={self.workout.id}")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data['workout_name'], "Morning Cardio Blast")
        self.assertTrue(response_get.data['all_completed'])

    def test_activity_list(self):
        # Create an activity
        Activity.objects.create(
            user=self.user,
            name="Run",
            duration=30,
            calories=150.0
        )
        response = self.client.get(self.activity_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_exercise_list(self):
        response = self.client.get(self.exercise_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_custom_routine_get_and_patch(self):
        # GET custom routine (auto-creates)
        response = self.client.get(self.custom_routine_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "My Custom Routine")
        
        # PATCH custom routine
        payload = {"name": "My New Routine", "description": "Updated description"}
        response_patch = self.client.patch(self.custom_routine_url, payload, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data['name'], "My New Routine")

    def test_toggle_custom_routine_exercise(self):
        payload = {"exercise_id": self.exercise.id}
        # Add exercise
        response = self.client.post(self.toggle_exercise_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], "added")
        
        # List exercises in routine
        response_list = self.client.get(self.custom_routine_exercises_url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)
        
        # Remove exercise by toggling again
        response_toggle_again = self.client.post(self.toggle_exercise_url, payload, format='json')
        self.assertEqual(response_toggle_again.status_code, status.HTTP_200_OK)
        self.assertEqual(response_toggle_again.data['action'], "removed")

    def test_complete_custom_routine_exercise(self):
        # 1. Add exercise to custom routine
        custom_routine = CustomRoutine.objects.create(user=self.user)
        custom_routine_exercise = CustomRoutineExercise.objects.create(
            custom_routine=custom_routine,
            exercise=self.exercise,
            sets=3,
            reps=10
        )
        
        payload = {
            "custom_routine_exercise_id": custom_routine_exercise.id,
            "actual_sets": 3,
            "actual_reps": 10,
            "duration_minutes": 5,
            "notes": "Done!"
        }
        
        response = self.client.post(self.complete_custom_exercise_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Exercise completed successfully")
        
        # Get completion history
        response_history = self.client.get(self.completion_history_url)
        self.assertEqual(response_history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_history.data), 1)

    def test_daily_progress(self):
        response = self.client.get(self.daily_progress_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('progress_percentage', response.data)
        self.assertIn('calories_burned', response.data)

    def test_workout_recommendation(self):
        # Set user goal and activity level
        self.user.goal = "weight_loss"
        self.user.activity_level = "beginner"
        self.user.save()
        
        response = self.client.get(self.recommendation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
