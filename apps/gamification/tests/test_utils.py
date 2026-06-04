from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.gamification.models import Rank, ActivityType, UserRank, PointTransaction, UserStreak
from apps.gamification.utils import (
    award_points, process_daily_checkin, get_user_stats,
    get_leaderboard_for_user, update_weekly_ranks
)

User = get_user_model()

class GamificationTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Ensure ranks exist (using get_or_create to avoid migration collisions)
        self.bronze_rank, _ = Rank.objects.get_or_create(
            name='BRONZE',
            defaults={
                'level': 1,
                'promotion_threshold': 30.0,
                'demotion_threshold': 0.0,
                'color_code': '#CD7F32'
            }
        )
        self.silver_rank, _ = Rank.objects.get_or_create(
            name='SILVER',
            defaults={
                'level': 2,
                'promotion_threshold': 25.0,
                'demotion_threshold': 20.0,
                'color_code': '#C0C0C0'
            }
        )
        
        # Ensure activity types exist
        self.checkin_activity, _ = ActivityType.objects.get_or_create(
            code='DAILY_CHECKIN',
            defaults={
                'name': 'Daily Check-in',
                'points': 10,
                'max_per_day': 1
            }
        )
        self.workout_activity, _ = ActivityType.objects.get_or_create(
            code='COMPLETE_WORKOUT',
            defaults={
                'name': 'Complete Workout',
                'points': 50,
                'max_per_day': 3
            }
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name="Test User",
            is_verified=True
        )
    
    def test_award_points(self):
        """Test awarding points to user"""
        success, message, points = award_points(
            user=self.user,
            activity_code='COMPLETE_WORKOUT'
        )
        
        self.assertTrue(success)
        self.assertEqual(points, 50)
        
        # Check user rank was created and updated
        user_rank = UserRank.objects.get(user=self.user)
        self.assertEqual(user_rank.total_points, 50)
        self.assertEqual(user_rank.weekly_points, 50)
        
        # Check transaction was recorded
        transaction = PointTransaction.objects.get(user=self.user)
        self.assertEqual(transaction.points, 50)
        self.assertEqual(transaction.activity_type, self.workout_activity)
    
    def test_daily_checkin(self):
        """Test daily check-in functionality"""
        success, message, points = process_daily_checkin(self.user)
        
        self.assertTrue(success)
        self.assertEqual(points, 10)
        
        # Check streak was created
        streak = UserStreak.objects.get(user=self.user)
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.total_check_ins, 1)
        
        # Try checking in again same day
        success, message, points = process_daily_checkin(self.user)
        self.assertFalse(success)
        self.assertEqual(points, 0)
    
    def test_max_per_day_limit(self):
        """Test that max_per_day limit is enforced"""
        # First check-in should work
        success1, _, points1 = award_points(self.user, 'DAILY_CHECKIN')
        self.assertTrue(success1)
        
        # Second check-in should fail (max_per_day=1)
        success2, message2, points2 = award_points(self.user, 'DAILY_CHECKIN')
        self.assertFalse(success2)
        self.assertEqual(points2, 0)
        self.assertIn('Daily limit', message2)
    
    def test_get_user_stats(self):
        """Test getting user statistics"""
        # Award some points first
        award_points(self.user, 'COMPLETE_WORKOUT')
        process_daily_checkin(self.user)
        
        stats = get_user_stats(self.user)
        
        self.assertEqual(stats['user']['username'], 'testuser')
        self.assertEqual(stats['points']['total'], 60)  # 50 + 10
        self.assertEqual(stats['points']['weekly'], 60)
        self.assertEqual(stats['rank']['level'], 1)
        self.assertEqual(stats['streak']['current'], 1)
    
    def test_leaderboard(self):
        """Test leaderboard functionality"""
        # Create another user with more points
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            full_name="Test User 2",
            is_verified=True
        )
        
        # Reset points for user rank to ensure clean test
        ur1 = UserRank.objects.get(user=self.user)
        ur1.total_points = 0
        ur1.weekly_points = 0
        ur1.save()

        ur2 = UserRank.objects.get(user=user2)
        ur2.total_points = 0
        ur2.weekly_points = 0
        ur2.save()

        award_points(self.user, 'COMPLETE_WORKOUT')  # 50 points
        award_points(user2, 'COMPLETE_WORKOUT')  # 50 points
        award_points(user2, 'COMPLETE_WORKOUT')  # 50 points (100 total)
        
        leaderboard = get_leaderboard_for_user(self.user)
        
        self.assertEqual(leaderboard['rank'], 'Bronze')
        self.assertEqual(leaderboard['total_users_in_rank'], 2)
        self.assertEqual(len(leaderboard['leaderboard']), 2)
        
        # user2 should be in first position
        self.assertEqual(leaderboard['leaderboard'][0]['user_id'], user2.id)
        self.assertEqual(leaderboard['leaderboard'][0]['position'], 1)
        
        # testuser should be in second position
        self.assertEqual(leaderboard['leaderboard'][1]['user_id'], self.user.id)
        self.assertEqual(leaderboard['leaderboard'][1]['position'], 2)
    
    def test_user_rank_auto_creation(self):
        """Test that UserRank is automatically created"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123',
            full_name="New User",
            is_verified=True
        )
        
        # UserRank should be created by signal
        self.assertTrue(UserRank.objects.filter(user=new_user).exists())
        
        user_rank = UserRank.objects.get(user=new_user)
        self.assertEqual(user_rank.current_rank, self.bronze_rank)
        self.assertEqual(user_rank.total_points, 0)
    
    def test_custom_points(self):
        """Test awarding custom points"""
        success, message, points = award_points(
            user=self.user,
            activity_code='COMPLETE_WORKOUT',
            custom_points=100
        )
        
        self.assertTrue(success)
        self.assertEqual(points, 100)
        
        user_rank = UserRank.objects.get(user=self.user)
        self.assertEqual(user_rank.total_points, 100)
