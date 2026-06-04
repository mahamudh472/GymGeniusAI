from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.gamification.models import Rank, ActivityType, UserRank, Challenge, UserChallengeProgress, PointTransaction, UserStreak

class GamificationViewsTests(APITestCase):
    def setUp(self):
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

        # Ensure activities exist
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

        # Create active verified user
        self.user = User.objects.create_user(
            email="gamifyuser@example.com",
            password="password123",
            full_name="Gamify User",
            is_verified=True
        )

        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "gamifyuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create Challenge
        self.now = timezone.now()
        self.challenge = Challenge.objects.create(
            name="Plank Challenge",
            description="Hold plank for 5 mins total",
            challenge_type="DAILY",
            difficulty="beginner",
            completion_points=100,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
            exercises=[
                {"name": "Plank Hold", "sets": 3, "rest_time": 60, "duration_seconds": 60}
            ],
            estimated_duration=5,
            estimated_calories=50,
            is_active=True
        )

        # URLs
        self.leaderboard_url = reverse('gamification:leaderboard')
        self.leaderboard_history_url = reverse('gamification:leaderboard-history')
        self.checkin_url = reverse('gamification:daily-checkin')
        self.award_points_url = reverse('gamification:award-points')
        self.challenge_list_url = reverse('gamification:challenge-list')
        self.challenge_detail_url = reverse('gamification:challenge-detail', kwargs={'pk': self.challenge.id})
        self.start_challenge_url = reverse('gamification:start-challenge')
        self.complete_exercise_url = reverse('gamification:complete-challenge-exercise')
        self.progress_url = reverse('gamification:user-challenge-progress')
        self.claim_reward_url = reverse('gamification:claim-challenge-reward')

    def test_leaderboard_and_history(self):
        # GET Leaderboard
        response = self.client.get(self.leaderboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # GET Leaderboard History
        response_hist = self.client.get(self.leaderboard_history_url)
        self.assertEqual(response_hist.status_code, status.HTTP_200_OK)
        self.assertTrue(response_hist.data['success'])

    def test_daily_checkin_success(self):
        response = self.client.post(self.checkin_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['points_awarded'], 10)

        # Verify streak exists
        streak = UserStreak.objects.get(user=self.user)
        self.assertEqual(streak.current_streak, 1)

    def test_daily_checkin_duplicate_denied(self):
        # Checkin first time
        self.client.post(self.checkin_url)
        # Checkin second time
        response = self.client.post(self.checkin_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_award_points_success(self):
        payload = {
            "activity_code": "COMPLETE_WORKOUT"
        }
        response = self.client.post(self.award_points_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['points_awarded'], 50)

    def test_challenge_list_and_detail(self):
        # List challenges
        response = self.client.get(self.challenge_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['name'], "Plank Challenge")

        # Retrieve challenge detail
        response_detail = self.client.get(self.challenge_detail_url)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_detail.data['data']['name'], "Plank Challenge")

    def test_challenge_flow(self):
        # 1. Start Challenge
        start_payload = {"challenge_id": self.challenge.id}
        response_start = self.client.post(self.start_challenge_url, start_payload, format='json')
        self.assertEqual(response_start.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response_start.data['success'])

        # Verify challenge progress is created
        self.assertTrue(UserChallengeProgress.objects.filter(user=self.user, challenge=self.challenge).exists())

        # Check progress endpoint
        response_progress = self.client.get(self.progress_url)
        self.assertEqual(response_progress.status_code, status.HTTP_200_OK)
        self.assertEqual(response_progress.data['count'], 1)
        self.assertEqual(response_progress.data['data'][0]['status'], 'IN_PROGRESS')

        # 2. Complete challenge exercise
        complete_payload = {
            "challenge_id": self.challenge.id,
            "exercise_index": 0,
            "notes": "Finished plank hold"
        }
        response_complete = self.client.post(self.complete_exercise_url, complete_payload, format='json')
        self.assertEqual(response_complete.status_code, status.HTTP_200_OK)
        self.assertTrue(response_complete.data['success'])
        self.assertTrue(response_complete.data['challenge_completed'])
        self.assertEqual(response_complete.data['points_awarded'], 100)

        # Verify progress status is COMPLETED
        progress = UserChallengeProgress.objects.get(user=self.user, challenge=self.challenge)
        self.assertEqual(progress.status, 'COMPLETED')

        # 3. Try to claim reward manually (should return message that it's already awarded/claimed)
        claim_payload = {"challenge_progress_id": progress.id}
        response_claim = self.client.post(self.claim_reward_url, claim_payload, format='json')
        # Check and award points on completed challenge returns false since it was already awarded
        self.assertEqual(response_claim.status_code, status.HTTP_400_BAD_REQUEST)
