"""
Test script for Custom Routine API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import Exercise, ExerciseCategory, CustomRoutine, CustomRoutineExercise

User = get_user_model()


class CustomRoutineAPITest(TestCase):
    def setUp(self):
        """Set up test client and create test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create test category
        self.category = ExerciseCategory.objects.create(
            name='Strength',
            description='Strength training exercises'
        )
        
        # Create test exercises
        self.exercise1 = Exercise.objects.create(
            name='Push-ups',
            description='Classic chest exercise',
            muscle_group='Chest',
            category=self.category,
            difficulty='beginner',
            default_sets=3,
            default_reps=10
        )
        
        self.exercise2 = Exercise.objects.create(
            name='Squats',
            description='Leg exercise',
            muscle_group='Legs',
            category=self.category,
            difficulty='intermediate',
            default_sets=4,
            default_reps=12
        )
        
        self.exercise3 = Exercise.objects.create(
            name='Pull-ups',
            description='Back exercise',
            muscle_group='Back',
            category=self.category,
            difficulty='advanced',
            default_sets=3,
            default_reps=8
        )
    
    def test_get_exercise_list(self):
        """Test getting list of all exercises"""
        response = self.client.get('/api/workouts/exercises/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'Pull-ups')  # Ordered by name
    
    def test_get_custom_routine_creates_if_not_exists(self):
        """Test that custom routine is created on first access"""
        # Verify no custom routine exists
        self.assertFalse(CustomRoutine.objects.filter(user=self.user).exists())
        
        # Get custom routine
        response = self.client.get('/api/workouts/custom-routine/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Custom Routine')
        self.assertEqual(response.data['exercise_count'], 0)
        
        # Verify custom routine was created
        self.assertTrue(CustomRoutine.objects.filter(user=self.user).exists())
    
    def test_toggle_add_exercise(self):
        """Test adding an exercise to custom routine"""
        # Add exercise
        response = self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'added')
        self.assertEqual(response.data['message'], f'Exercise "{self.exercise1.name}" added to custom routine')
        self.assertIsNotNone(response.data['exercise'])
        self.assertEqual(response.data['custom_routine']['exercise_count'], 1)
        
        # Verify exercise was added
        custom_routine = CustomRoutine.objects.get(user=self.user)
        self.assertEqual(custom_routine.exercises.count(), 1)
        self.assertEqual(custom_routine.exercises.first().exercise, self.exercise1)
    
    def test_toggle_remove_exercise(self):
        """Test removing an exercise from custom routine"""
        # First add an exercise
        custom_routine = CustomRoutine.objects.create(user=self.user)
        CustomRoutineExercise.objects.create(
            custom_routine=custom_routine,
            exercise=self.exercise1,
            order=1
        )
        
        # Remove exercise
        response = self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'removed')
        self.assertEqual(response.data['message'], f'Exercise "{self.exercise1.name}" removed from custom routine')
        self.assertIsNone(response.data['exercise'])
        self.assertEqual(response.data['custom_routine']['exercise_count'], 0)
        
        # Verify exercise was removed
        self.assertEqual(custom_routine.exercises.count(), 0)
    
    def test_toggle_multiple_exercises(self):
        """Test adding multiple exercises maintains order"""
        # Add first exercise
        self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        # Add second exercise
        self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise2.id},
            format='json'
        )
        
        # Add third exercise
        response = self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise3.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_routine']['exercise_count'], 3)
        
        # Get custom routine exercises
        response = self.client.get('/api/workouts/custom-routine/exercises/')
        
        self.assertEqual(len(response.data), 3)
        # Verify order
        self.assertEqual(response.data[0]['order'], 1)
        self.assertEqual(response.data[1]['order'], 2)
        self.assertEqual(response.data[2]['order'], 3)
    
    def test_cannot_add_duplicate_exercise(self):
        """Test that the same exercise cannot be added twice"""
        # Add exercise first time
        self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        # Try to add same exercise again (should remove it)
        response = self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'removed')
        self.assertEqual(response.data['custom_routine']['exercise_count'], 0)
    
    def test_list_custom_routine_exercises(self):
        """Test listing custom routine exercises"""
        # Create custom routine with exercises
        custom_routine = CustomRoutine.objects.create(user=self.user)
        CustomRoutineExercise.objects.create(
            custom_routine=custom_routine,
            exercise=self.exercise1,
            order=1
        )
        CustomRoutineExercise.objects.create(
            custom_routine=custom_routine,
            exercise=self.exercise2,
            order=2
        )
        
        # Get exercises list
        response = self.client.get('/api/workouts/custom-routine/exercises/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['exercise_name'], self.exercise1.name)
        self.assertEqual(response.data[1]['exercise_name'], self.exercise2.name)
    
    def test_update_custom_routine_details(self):
        """Test updating custom routine name and description"""
        # Create custom routine
        CustomRoutine.objects.create(user=self.user)
        
        # Update details
        response = self.client.patch(
            '/api/workouts/custom-routine/',
            {
                'name': 'Morning Strength Routine',
                'description': 'My go-to morning workout'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Morning Strength Routine')
        self.assertEqual(response.data['description'], 'My go-to morning workout')
    
    def test_exercise_defaults_are_applied(self):
        """Test that exercise default values are applied to custom routine exercise"""
        # Add exercise
        self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': self.exercise1.id},
            format='json'
        )
        
        # Get exercise details
        response = self.client.get('/api/workouts/custom-routine/exercises/')
        
        exercise_data = response.data[0]
        self.assertEqual(exercise_data['sets'], self.exercise1.default_sets)
        self.assertEqual(exercise_data['reps'], self.exercise1.default_reps)
        self.assertEqual(exercise_data['rest_time'], self.exercise1.default_rest_time)
    
    def test_toggle_invalid_exercise_id(self):
        """Test toggling with invalid exercise ID"""
        response = self.client.post(
            '/api/workouts/custom-routine/toggle-exercise/',
            {'exercise_id': 99999},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_filter_exercises_by_muscle_group(self):
        """Test filtering exercises by muscle group"""
        response = self.client.get('/api/workouts/exercises/?muscle_group=Chest')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Push-ups')
    
    def test_filter_exercises_by_difficulty(self):
        """Test filtering exercises by difficulty"""
        response = self.client.get('/api/workouts/exercises/?difficulty=beginner')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['difficulty'], 'beginner')


if __name__ == '__main__':
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['workouts.tests'])
