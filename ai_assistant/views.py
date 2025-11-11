from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import AIConversation, ConversationMessage
from .serializers import AIConversationSerializer, UserInputSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsActiveUser
from .utils import fitness_coach_ai

class ConversationMessageView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AIConversationSerializer
        elif self.request.method == 'POST':
            return UserInputSerializer

    def get(self, request, *args, **kwargs):
        conversation, created = AIConversation.objects.get_or_create(user=request.user)
        serializer = self.get_serializer_class()(conversation)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        input_serializer = UserInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_input = input_serializer.validated_data['user_input']
        ai_response = self.generate_ai_response(user_input, user=request.user)
        ConversationMessage.objects.create(
            conversation=AIConversation.objects.get(user=request.user),
            sender='user',
            message=user_input
        )
        ConversationMessage.objects.create(
            conversation=AIConversation.objects.get(user=request.user),
            sender='ai',
            message=ai_response
        )
        context = {
            'user_input': user_input,
            'ai_response': ai_response
        }
        return Response(context)
    
    def generate_ai_response(self, user_input, user):
        result = fitness_coach_ai(
            gender=user.gender,
            age=user.age,
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            goal=user.goal,
            activity_level=user.activity_level,
            username=user.username,
            coach_name=user.coach_type.name,
            current_query=user_input
        )
        return result['reply']


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