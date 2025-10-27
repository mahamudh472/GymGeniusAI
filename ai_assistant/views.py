from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import AIConversation
from .serializers import AIConversationSerializer, UserInputSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsActiveUser

class ConversationView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AIConversationSerializer
        elif self.request.method == 'POST':
            return UserInputSerializer
        
    def get(self, request, *args, **kwargs):
        # Logic to retrieve conversation history or initial prompt
        conversation, created = AIConversation.objects.get_or_create(user=request.user)
        print("Conversation:", conversation)
        serializer = self.get_serializer_class()(conversation)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        input_serializer = UserInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_input = input_serializer.validated_data['user_input']
        ai_response = self.generate_ai_response(user_input)
        context = {
            'user_input': user_input,
            'ai_response': ai_response
        }
        return Response(context)
    
    def generate_ai_response(self, user_input):
        # Placeholder for AI response generation logic
        return f"AI response to: {user_input}"