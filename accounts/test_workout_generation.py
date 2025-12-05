from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from accounts.signals import check_and_generate_workouts
from accounts.tasks import generate_initial_workouts_task

User = get_user_model()


class WorkoutGenerationTestCase(TestCase):
    """Test automatic workout generation on user profile completion"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_incomplete_profile_does_not_trigger_task(self):
        """Test that incomplete profile doesn't trigger workout generation"""
        with patch('accounts.signals.generate_initial_workouts_task') as mock_task:
            # Update with incomplete data
            self.user.gender = 'male'
            self.user.save()
            
            # Task should not be called
            mock_task.apply_async.assert_not_called()

    def test_complete_profile_triggers_task(self):
        """Test that completing profile triggers workout generation"""
        with patch('accounts.signals.generate_initial_workouts_task') as mock_task:
            # Complete the profile
            self.user.gender = 'male'
            self.user.age = 25
            self.user.weight_kg = 75.0
            self.user.height_cm = 180.0
            self.user.goal = 'weight_loss'
            self.user.activity_level = 'intermediate'
            self.user.save()
            
            # Task should be called
            mock_task.apply_async.assert_called_once()

    def test_already_generated_workouts_not_triggered(self):
        """Test that workouts are not regenerated if already done"""
        with patch('accounts.signals.generate_initial_workouts_task') as mock_task:
            # Mark workouts as already generated
            self.user.initial_workouts_generated = True
            self.user.gender = 'male'
            self.user.age = 25
            self.user.save()
            
            # Task should not be called
            mock_task.apply_async.assert_not_called()

    @patch('accounts.tasks.generate_multi_level_workouts')
    @patch('accounts.tasks.generate_workouts_for_user')
    def test_task_generates_workouts(self, mock_gen_workouts, mock_multi_level):
        """Test that the celery task successfully generates workouts"""
        # Setup user with complete profile
        self.user.gender = 'male'
        self.user.age = 25
        self.user.weight_kg = 75.0
        self.user.height_cm = 180.0
        self.user.goal = 'weight_loss'
        self.user.activity_level = 'intermediate'
        self.user.full_name = 'Test User'
        self.user.save()

        # Mock the workout generation
        mock_multi_level.return_value = {
            'workout_levels': [
                {'workout_name': 'Beginner', 'exercises': []},
                {'workout_name': 'Intermediate', 'exercises': []},
                {'workout_name': 'Advanced', 'exercises': []},
            ]
        }

        # Run the task
        result = generate_initial_workouts_task(str(self.user.id))

        # Verify the result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['workout_count'], 3)

        # Verify user flag was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.initial_workouts_generated)

    def test_task_skips_if_already_generated(self):
        """Test that task skips if workouts already generated"""
        self.user.initial_workouts_generated = True
        self.user.save()

        result = generate_initial_workouts_task(str(self.user.id))

        self.assertEqual(result['status'], 'skipped')
