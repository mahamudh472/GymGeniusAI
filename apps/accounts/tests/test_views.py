from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.accounts.models import User, OTP, Coach, SubscriptionPlan, UserSubscription
from apps.workouts.models import UserWorkout
from apps.articles.models import Article

class AccountsViewsTests(APITestCase):
    def setUp(self):
        # Create a default user
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            full_name="Default User",
            is_verified=True
        )
        
        # Paths/URLs
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.register_url = reverse('register')
        self.verify_email_url = reverse('verify_email')
        self.send_otp_url = reverse('password_reset')  # points to SendOTPView
        self.password_reset_confirm_url = reverse('password_reset_confirm')
        self.change_password_url = reverse('change_password')
        self.profile_url = reverse('profile')
        self.profile_update_url = reverse('profile_update')
        self.coach_list_url = reverse('coach_list')
        self.home_api_url = reverse('home_api')
        self.subscription_plans_url = reverse('subscription_plans')
        self.delete_account_url = reverse('delete_account')

    def get_jwt_token(self, email="user@example.com", password="password123"):
        response = self.client.post(self.login_url, {"email": email, "password": password})
        return response.data.get('access'), response.data.get('refresh')

    def authenticate_client(self):
        access_token, _ = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_login_success(self):
        response = self.client.post(self.login_url, {"email": "user@example.com", "password": "password123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {"email": "user@example.com", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_success(self):
        # Clear outbox
        mail.outbox = []
        
        payload = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        
        # Verify user is created but unverified
        new_user = User.objects.get(email="newuser@example.com")
        self.assertFalse(new_user.is_verified)
        
        # Verify OTP is created
        otp_exists = OTP.objects.filter(user=new_user, purpose='signup').exists()
        self.assertTrue(otp_exists)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify your email", mail.outbox[0].subject)

    def test_verify_email_success(self):
        # Create unverified user and OTP
        unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password="password123",
            full_name="Unverified User",
            is_verified=False
        )
        otp = OTP.objects.create(
            user=unverified_user,
            code="1234",
            purpose="signup",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        payload = {
            "email": "unverified@example.com",
            "otp": "1234"
        }
        response = self.client.post(self.verify_email_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is now verified
        unverified_user.refresh_from_db()
        self.assertTrue(unverified_user.is_verified)
        
        # Verify OTP is marked as used
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_verify_email_invalid_otp(self):
        unverified_user = User.objects.create_user(
            email="unverified2@example.com",
            password="password123",
            full_name="Unverified User 2",
            is_verified=False
        )
        OTP.objects.create(
            user=unverified_user,
            code="1234",
            purpose="signup",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        payload = {
            "email": "unverified2@example.com",
            "otp": "9999"  # incorrect
        }
        response = self.client.post(self.verify_email_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_otp_password_reset(self):
        mail.outbox = []
        payload = {
            "email": "user@example.com",
            "purpose": "password_reset"
        }
        response = self.client.post(self.send_otp_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify OTP created
        self.assertTrue(OTP.objects.filter(user=self.user, purpose='password_reset').exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_confirm_success(self):
        otp = OTP.objects.create(
            user=self.user,
            code="5678",
            purpose="password_reset",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        payload = {
            "email": "user@example.com",
            "otp": "5678",
            "new_password": "newpassword456"
        }
        response = self.client.post(self.password_reset_confirm_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password is changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_change_password_success(self):
        self.authenticate_client()
        payload = {
            "old_password": "password123",
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }
        response = self.client.post(self.change_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_profile_retrieve_success(self):
        self.authenticate_client()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), "user@example.com")
        self.assertEqual(response.data.get('full_name'), "Default User")

    def test_profile_update_success(self):
        self.authenticate_client()
        payload = {
            "full_name": "Updated Default User"
        }
        response = self.client.patch(self.profile_update_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Default User")

    def test_coach_list(self):
        self.authenticate_client()
        # Create some coaches
        Coach.objects.create(
            name="Coach John",
            behavior="Friendly motivator"
        )
        response = self.client.get(self.coach_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Coach John")

    def test_home_api(self):
        self.authenticate_client()
        # Create a workout and an article
        UserWorkout.objects.create(
            user=self.user,
            name="Morning Cardio"
        )
        Article.objects.create(
            title="Importance of Hydration",
            description="Hydrate well",
            content="Drink more water.",
            category="tips",
            created_by=self.user
        )
        
        response = self.client.get(self.home_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('workouts', response.data)
        self.assertIn('articles', response.data)
        self.assertEqual(len(response.data['workouts']), 1)
        self.assertEqual(len(response.data['articles']), 1)

    def test_subscription_plans(self):
        # Create a plan
        SubscriptionPlan.objects.create(
            name="Pro Plan",
            product_id="pro_plan",
            price=19.99,
            duration_days=30,
            features={"premium_workouts": True}
        )
        
        response = self.client.get(self.subscription_plans_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Pro Plan")

    def test_logout_success(self):
        _, refresh_token = self.get_jwt_token()
        self.authenticate_client()
        
        payload = {
            "refresh_token": str(refresh_token)
        }
        response = self.client.post(self.logout_url, payload)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_delete_account_success(self):
        self.authenticate_client()
        response = self.client.delete(self.delete_account_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is deleted
        self.assertFalse(User.objects.filter(email="user@example.com").exists())
