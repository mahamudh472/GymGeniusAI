from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import AIConversation, ConversationMessage
from .serializers import AIConversationSerializer, UserInputSerializer
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsActiveUser
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
        
        # Validate required user attributes
        user = request.user
        if not all([user.gender, user.age, user.weight_kg, user.height_cm, user.goal, user.activity_level]):
            return Response({
                "error": "Please complete your profile with gender, age, weight, height, goal, and activity level before using AI assistant."
            }, status=400)
        
        if not user.coach_type:
            return Response({
                "error": "Please select a coach type in your profile before using AI assistant."
            }, status=400)
        
        try:
            ai_response = self.generate_ai_response(user_input, user=user)
        except Exception as e:
            return Response({
                "error": "AI assistant is temporarily unavailable. Please try again later.",
                "detail": str(e) if request.user.is_staff else None
            }, status=500)
        
        try:
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
        except Exception as e:
            pass
        context = {
            'user_input': user_input,
            'ai_response': ai_response
        }
        return Response(context)
    
    def generate_ai_response(self, user_input, user):
        try:
            conversation = AIConversation.objects.get(user=user)
            result = fitness_coach_ai(
                gender=user.gender,
                age=user.age,
                weight_kg=user.weight_kg,
                height_cm=user.height_cm,
                goal=user.goal,
                activity_level=user.activity_level,
                username=user.username,
                coach_name=user.coach_type.name if user.coach_type else "Chris",
                current_query=user_input,
                conversation_history=conversation.get_conversation_history()
            )
            return result.get('reply', 'Sorry, I could not process your request.')
        except Exception as e:
            raise


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
    


    # class TestView(GenericAPIView):
    #     # permission_classes = [IsAuthenticated, IsActiveUser]
    #     permission_classes = []

    #     def get(self, request, *args, **kwargs):
    #         from .utils import generate_dataset_based_workout, generate_multi_level_workouts
    #         from apps.workouts.utils import generate_workouts_for_user
    #         user = request.user

    #         response = generate_multi_level_workouts(
    #             gender=user.gender,
    #             age=user.age,
    #             weight_kg=user.weight_kg,
    #             height_cm=user.height_cm,
    #             goal=user.goal,
    #             activity_level=user.activity_level,
    #             username=user.profile_name
    #         )
    #         workouts = response['workout_levels']
    #         with open("debug_workouts.json", "w") as f:
    #             import json
    #             json.dump(workouts, f, indent=4)

    #         generate_workouts_for_user(workout_list=workouts, user=user)
            
    #         return Response({"message": "Test view is working!", "workout": workouts})
