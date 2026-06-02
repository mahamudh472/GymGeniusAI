from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from accounts.models import User, SubscriptionPlan, UserSubscription

class RevenueCatWebhookTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        # Create a test subscription plan
        self.plan = SubscriptionPlan.objects.create(
            name="Premium Monthly",
            product_id="premium_monthly",
            price=9.99,
            duration_days=30,
            features={"ai_coach": True}
        )
        
        self.webhook_url = reverse('revenuecat_webhook')
        
        # Set a test authorization token on settings override
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            self.valid_headers = {"HTTP_AUTHORIZATION": "Bearer test_secret_token"}
        self.invalid_headers = {"HTTP_AUTHORIZATION": "Bearer wrong_token"}

    def test_webhook_unauthorized_with_wrong_token(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            payload = {"event": {"type": "INITIAL_PURCHASE"}}
            response = self.client.post(self.webhook_url, payload, format='json', **self.invalid_headers)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_unauthorized_with_missing_token(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            payload = {"event": {"type": "INITIAL_PURCHASE"}}
            response = self.client.post(self.webhook_url, payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_invalid_payload(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            response = self.client.post(self.webhook_url, {}, format='json', **self.valid_headers)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_initial_purchase(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            purchased_at = timezone.now()
            expiration_at = purchased_at + timezone.timedelta(days=30)
            
            payload = {
                "event": {
                    "id": "event_id_123",
                    "type": "INITIAL_PURCHASE",
                    "app_user_id": str(self.user.id),
                    "product_id": "premium_monthly",
                    "purchased_at_ms": int(purchased_at.timestamp() * 1000),
                    "expiration_at_ms": int(expiration_at.timestamp() * 1000)
                }
            }
            
            response = self.client.post(self.webhook_url, payload, format='json', **self.valid_headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify user subscription was created
            user_sub = UserSubscription.objects.get(user=self.user, plan=self.plan)
            self.assertTrue(user_sub.is_active)
            self.assertEqual(user_sub.payment_status, 'completed')
            self.assertEqual(user_sub.transaction_id, 'event_id_123')
            self.assertEqual(user_sub.start_date, purchased_at.date())
            self.assertEqual(user_sub.end_date, expiration_at.date())
            
            # Verify user's active subscription property and subscription_id field
            self.user.refresh_from_db()
            self.assertTrue(self.user.has_active_subscription)
            self.assertEqual(self.user.subscription_id, self.plan.id)

    def test_webhook_renewal(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            # Setup initial subscription
            purchased_at_1 = timezone.now() - timezone.timedelta(days=30)
            expiration_at_1 = purchased_at_1 + timezone.timedelta(days=30)
            
            user_sub = UserSubscription.objects.create(
                user=self.user,
                plan=self.plan,
                start_date=purchased_at_1.date(),
                end_date=expiration_at_1.date(),
                is_active=True,
                payment_status='completed',
                transaction_id='event_id_123'
            )
            self.user.subscription_id = self.plan.id
            self.user.save()
            
            # Renewal event payload
            purchased_at_2 = expiration_at_1
            expiration_at_2 = purchased_at_2 + timezone.timedelta(days=30)
            
            payload = {
                "event": {
                    "id": "event_id_456",
                    "type": "RENEWAL",
                    "app_user_id": str(self.user.id),
                    "product_id": "premium_monthly",
                    "purchased_at_ms": int(purchased_at_2.timestamp() * 1000),
                    "expiration_at_ms": int(expiration_at_2.timestamp() * 1000)
                }
            }
            
            response = self.client.post(self.webhook_url, payload, format='json', **self.valid_headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify user subscription was updated
            user_sub.refresh_from_db()
            self.assertTrue(user_sub.is_active)
            self.assertEqual(user_sub.transaction_id, 'event_id_456')
            self.assertEqual(user_sub.start_date, purchased_at_2.date())
            self.assertEqual(user_sub.end_date, expiration_at_2.date())
            
            # Verify user model settings
            self.user.refresh_from_db()
            self.assertTrue(self.user.has_active_subscription)
            self.assertEqual(self.user.subscription_id, self.plan.id)

    def test_webhook_expiration(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            # Setup active subscription
            user_sub = UserSubscription.objects.create(
                user=self.user,
                plan=self.plan,
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                is_active=True,
                payment_status='completed'
            )
            self.user.subscription_id = self.plan.id
            self.user.save()
            
            # Expiration event payload
            payload = {
                "event": {
                    "id": "event_id_789",
                    "type": "EXPIRATION",
                    "app_user_id": str(self.user.id),
                    "product_id": "premium_monthly"
                }
            }
            
            response = self.client.post(self.webhook_url, payload, format='json', **self.valid_headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify subscription is now inactive
            user_sub.refresh_from_db()
            self.assertFalse(user_sub.is_active)
            
            # Verify user model reflects expiration
            self.user.refresh_from_db()
            self.assertFalse(self.user.has_active_subscription)
            self.assertIsNone(self.user.subscription_id)

    def test_webhook_refund(self):
        with self.settings(REVENUECAT_WEBHOOK_AUTH_TOKEN="test_secret_token"):
            # Setup active subscription
            user_sub = UserSubscription.objects.create(
                user=self.user,
                plan=self.plan,
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                is_active=True,
                payment_status='completed'
            )
            self.user.subscription_id = self.plan.id
            self.user.save()
            
            # Refund event payload
            payload = {
                "event": {
                    "id": "event_id_abc",
                    "type": "REFUND",
                    "app_user_id": str(self.user.id),
                    "product_id": "premium_monthly"
                }
            }
            
            response = self.client.post(self.webhook_url, payload, format='json', **self.valid_headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify subscription is now inactive and refunded
            user_sub.refresh_from_db()
            self.assertFalse(user_sub.is_active)
            self.assertEqual(user_sub.payment_status, 'refunded')
            
            # Verify user model reflects refund
            self.user.refresh_from_db()
            self.assertFalse(self.user.has_active_subscription)
            self.assertIsNone(self.user.subscription_id)
