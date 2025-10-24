from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import AIConversation
from .serializers import AIConversationSerializer, AIConversationDetailSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsActiveUser

class ConversationView(GenericAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, *args, **kwargs):
        # Logic to retrieve conversation history or initial prompt
        conversation, created = AIConversation.objects.get_or_create(user=request.user)
        print("Conversation:", conversation)
        serializer = self.serializer_class(conversation)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Logic to process user input and generate AI response
        user_input = request.data.get('user_input')
        ai_response = self.generate_ai_response(user_input)
        context = {
            'user_input': user_input,
            'ai_response': ai_response
        }
        return Response(context)
    def generate_ai_response(self, user_input):
        # Placeholder for AI response generation logic
        return f"AI response to: {user_input}"