from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from articles.models import Article, WorkoutVideo

class ArticlesViewsTests(APITestCase):
    def setUp(self):
        # Create standard user and admin user
        self.user = User.objects.create_user(
            email="articlesuser@example.com",
            password="password123",
            full_name="Standard User",
            is_verified=True
        )
        self.admin_user = User.objects.create_user(
            email="adminuser@example.com",
            password="password123",
            full_name="Admin User",
            is_staff=True,
            is_verified=True
        )

        # Create test article and workout video
        self.article = Article.objects.create(
            title="Cardio Tips",
            description="Cardio workout advice",
            content="Do running and swimming.",
            category="fitness",
            created_by=self.admin_user
        )
        self.video = WorkoutVideo.objects.create(
            video_url="https://example.com/video.mp4",
            title="Stretching Exercises",
            description="Stretching routine video",
            duration_minutes=15
        )

        # URLs
        self.article_list_url = reverse('article-list')
        self.article_create_url = reverse('article-create')
        self.article_detail_url = reverse('article-detail', kwargs={'id': self.article.id})
        self.video_list_url = reverse('workoutvideo-list')
        self.video_detail_url = reverse('workoutvideo-detail', kwargs={'id': self.video.id})

    def test_list_articles(self):
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Cardio Tips")

    def test_article_detail(self):
        response = self.client.get(self.article_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Cardio Tips")

    def test_create_article_denied_for_standard_user(self):
        # Authenticate standard user
        login_url = reverse('login')
        login_response = self.client.post(login_url, {"email": "articlesuser@example.com", "password": "password123"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data.get("access")}')

        payload = {
            "title": "New Workout Plan",
            "description": "Advice on lifting",
            "content": "Focus on compound exercises.",
            "category": "fitness"
        }
        response = self.client.post(self.article_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_article_allowed_for_admin(self):
        # Authenticate admin user
        login_url = reverse('login')
        login_response = self.client.post(login_url, {"email": "adminuser@example.com", "password": "password123"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data.get("access")}')

        payload = {
            "title": "New Workout Plan",
            "description": "Advice on lifting",
            "content": "Focus on compound exercises.",
            "category": "fitness"
        }
        response = self.client.post(self.article_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Workout Plan")
        self.assertTrue(Article.objects.filter(title="New Workout Plan").exists())

    def test_list_workout_videos(self):
        response = self.client.get(self.video_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Stretching Exercises")

    def test_workout_video_detail(self):
        response = self.client.get(self.video_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Stretching Exercises")
