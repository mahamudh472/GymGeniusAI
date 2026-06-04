from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
from io import BytesIO
from PIL import Image

from apps.accounts.models import User
from apps.workouts.models import UserWorkout
from apps.articles.models import Article
from apps.utils.models import Favorite, FAQ, ContactOption, Notification, PrivacyPolicy, NotificationSetting
from fcm_django.models import FCMDevice

def generate_valid_image():
    file_obj = BytesIO()
    image = Image.new("RGB", (1, 1), color="blue")
    image.save(file_obj, "jpeg")
    file_obj.seek(0)
    return SimpleUploadedFile("icon.jpg", file_obj.read(), content_type="image/jpeg")

class UtilsViewsTests(APITestCase):
    def setUp(self):
        # Create active verified user
        self.user = User.objects.create_user(
            email="utilsuser@example.com",
            password="password123",
            full_name="Utils User",
            is_verified=True
        )

        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "utilsuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create FAQ
        self.faq = FAQ.objects.create(
            question="How to reset password?",
            answer="Go to settings.",
            type="account"
        )

        # Create ContactOption
        icon = generate_valid_image()
        self.contact_option = ContactOption.objects.create(
            name="Support Email",
            icon=icon,
            link="mailto:support@gymgenius.ai"
        )

        # Create PrivacyPolicy
        self.privacy_policy = PrivacyPolicy.objects.create(
            content="Our privacy policy details.",
        )

        # Create Workout for favorites & search
        self.workout = UserWorkout.objects.create(
            user=self.user,
            name="Super Strength Session",
            description="Powerlifting basics",
            difficulty="intermediate",
            estimated_duration=45,
            estimated_calories=300
        )

        # Create Article for favorites & search
        self.article = Article.objects.create(
            title="Importance of Hydration",
            content="Always drink water before and after exercise.",
            created_by=self.user
        )

        # Create Notification
        self.notification = Notification.objects.create(
            user=self.user,
            title="Welcome!",
            message="Welcome to GymGeniusAI",
            notification_type="system",
            is_read=False
        )

        # URLs
        self.faq_list_url = reverse('faq-list')
        self.contact_option_list_url = reverse('contact-option-list')
        self.privacy_policy_url = reverse('privacy-policy')
        self.privacy_policy_view_url = reverse('privacy-policy-view')
        self.favorite_list_url = reverse('favorite-list')
        self.favorite_toggle_url = reverse('favorite-toggle')
        self.search_results_url = reverse('search-results')
        self.notification_list_url = reverse('notification-list')
        self.notification_detail_url = reverse('notification-detail', kwargs={'pk': self.notification.id})
        self.mark_all_read_url = reverse('mark-all-read')
        self.register_device_url = reverse('register-device-token')
        self.unregister_device_url = reverse('unregister-device-token')
        self.create_demo_notification_url = reverse('create-demo-notification')
        self.notification_settings_url = reverse('notification-settings')

    def test_faq_list(self):
        response = self.client.get(self.faq_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], "How to reset password?")

    def test_contact_option_list(self):
        response = self.client.get(self.contact_option_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Support Email")

    def test_privacy_policy_json(self):
        response = self.client.get(self.privacy_policy_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Our privacy policy details.")

    def test_privacy_policy_web_view(self):
        response = self.client.get(self.privacy_policy_view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Our privacy policy details.")

    def test_privacy_policy_not_found(self):
        PrivacyPolicy.objects.all().delete()
        response_json = self.client.get(self.privacy_policy_url)
        self.assertEqual(response_json.status_code, status.HTTP_404_NOT_FOUND)

        response_web = self.client.get(self.privacy_policy_view_url)
        self.assertEqual(response_web.status_code, 404)

    def test_favorite_toggle_and_list(self):
        # 1. Initially favorites list is empty
        response = self.client.get(self.favorite_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # 2. Add workout to favorites
        payload = {
            "content_type": "userworkout",
            "object_id": self.workout.id
        }
        response_toggle = self.client.post(self.favorite_toggle_url, payload, format='json')
        self.assertEqual(response_toggle.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_toggle.data['detail'], "Added to favorites.")

        # Verify favorites list contains it
        response_list = self.client.get(self.favorite_list_url)
        self.assertEqual(len(response_list.data), 1)
        self.assertEqual(response_list.data[0]['type'], "userworkout")
        self.assertEqual(response_list.data[0]['object']['name'], "Super Strength Session")

        # 3. Toggle again (remove from favorites)
        response_remove = self.client.post(self.favorite_toggle_url, payload, format='json')
        self.assertEqual(response_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(response_remove.data['detail'], "Removed from favorites.")

        # Verify favorites list is empty again
        response_list_empty = self.client.get(self.favorite_list_url)
        self.assertEqual(len(response_list_empty.data), 0)

    def test_search_results(self):
        # Search workouts/articles matching 'Strength'
        response = self.client.get(f"{self.search_results_url}?q=Strength")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['workouts']), 1)
        self.assertEqual(response.data['workouts'][0]['name'], "Super Strength Session")
        self.assertEqual(len(response.data['articles']), 0)

        # Search matching 'Hydration'
        response_article = self.client.get(f"{self.search_results_url}?q=Hydration")
        self.assertEqual(response_article.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_article.data['workouts']), 0)
        self.assertEqual(len(response_article.data['articles']), 1)
        self.assertEqual(response_article.data['articles'][0]['title'], "Importance of Hydration")

    def test_notification_list(self):
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Welcome!")

    def test_notification_detail_post(self):
        # Post creates a notification
        payload = {
            "title": "Alert",
            "message": "Drink water",
            "notification_type": "reminder"
        }
        response = self.client.post(self.notification_detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Alert")
        self.assertTrue(Notification.objects.filter(title="Alert").exists())

    def test_mark_all_notifications_read(self):
        self.assertFalse(self.notification.is_read)
        response = self.client.post(self.mark_all_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_register_and_unregister_device_token(self):
        payload = {"device_token": "some-fcm-device-token"}
        response = self.client.post(self.register_device_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(FCMDevice.objects.filter(user=self.user, registration_id="some-fcm-device-token").exists())

        # Unregister
        response_unreg = self.client.post(self.unregister_device_url)
        self.assertEqual(response_unreg.status_code, status.HTTP_200_OK)
        self.assertTrue(response_unreg.data['success'])
        self.assertFalse(FCMDevice.objects.filter(user=self.user).exists())

    @patch('apps.utils.views.FCMDevice.send_message')
    def test_create_demo_notification(self, mock_send_message):
        # This will trigger add_notification
        response = self.client.post(self.create_demo_notification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify notification created
        self.assertTrue(Notification.objects.filter(user=self.user, title="Demo Notification").exists())

    def test_notification_settings_get_and_update(self):
        # GET notification settings
        response = self.client.get(self.notification_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['general_notifications'])

        # UPDATE notification settings
        payload = {
            "general_notifications": False,
            "sound": False,
            "do_not_disturb": True
        }
        response_update = self.client.patch(self.notification_settings_url, payload, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertFalse(response_update.data['general_notifications'])
        self.assertFalse(response_update.data['sound'])
        self.assertTrue(response_update.data['do_not_disturb'])
