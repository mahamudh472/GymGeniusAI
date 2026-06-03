from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import User, Coach
from ai_assistant.models import AIConversation, ConversationMessage

class AIAssistantViewsTests(APITestCase):
    def setUp(self):
        # Create coach
        self.coach = Coach.objects.create(
            name="Chris",
            behavior="Aggressive motivator"
        )

        # Create active verified user
        self.user = User.objects.create_user(
            email="aiuser@example.com",
            password="password123",
            full_name="AI User",
            is_verified=True,
            gender="male",
            age=25,
            weight_kg=75.0,
            height_cm=180.0,
            goal="weight_loss",
            activity_level="beginner",
            coach_type=self.coach
        )
        
        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "aiuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # URLs
        self.conversation_url = reverse('ai_assistant:conversation-message')

    def test_get_conversation_history(self):
        conversation = AIConversation.objects.create(user=self.user)
        ConversationMessage.objects.create(
            conversation=conversation,
            sender="user",
            message="Hello Coach!"
        )
        ConversationMessage.objects.create(
            conversation=conversation,
            sender="ai",
            message="Hello! Ready to train?"
        )

        response = self.client.get(self.conversation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)
        self.assertEqual(len(response.data['messages']), 2)

    def test_post_message_profile_incomplete(self):
        # Create user with incomplete profile
        incomplete_user = User.objects.create_user(
            email="incomplete@example.com",
            password="password123",
            full_name="Incomplete User",
            is_verified=True
            # fields like gender, age, etc. are empty
        )
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "incomplete@example.com", "password": "password123"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data.get("access")}')

        payload = {"user_input": "What should I eat today?"}
        response_post = self.client.post(self.conversation_url, payload, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("complete your profile", response_post.data['error'])

    @patch('ai_assistant.views.fitness_coach_ai')
    def test_post_message_success(self, mock_coach_ai):
        mock_coach_ai.return_value = {
            'reply': 'Keep pushing hard, you are doing great!'
        }

        # Ensure conversation exists
        AIConversation.objects.get_or_create(user=self.user)

        # User is already fully populated from setUp
        payload = {"user_input": "How do I lose weight?"}
        response = self.client.post(self.conversation_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ai_response'], 'Keep pushing hard, you are doing great!')

        # Verify messages saved
        conversation = AIConversation.objects.get(user=self.user)
        messages = ConversationMessage.objects.filter(conversation=conversation).order_by('timestamp')
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].sender, 'user')
        self.assertEqual(messages[0].message, 'How do I lose weight?')
        self.assertEqual(messages[1].sender, 'ai')
        self.assertEqual(messages[1].message, 'Keep pushing hard, you are doing great!')
