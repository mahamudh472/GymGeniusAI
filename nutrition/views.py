from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, inline_serializer

from accounts.permissions import IsActiveUser
from nutrition.models import UserUploadedMeal
from ai_assistant.utils import analyze_single_meal
from nutrition.tasks import analyze_uploaded_meal


def calculate_meal_streak(user):
    """
    Calculate the consecutive days streak of meal uploads for a user.
    Counts backward from today to find the last consecutive upload days.
    """
    # Get all unique dates when user uploaded meals, ordered descending
    upload_dates = UserUploadedMeal.objects.filter(
        user=user
    ).dates('created_at', 'day', order='DESC')
    
    if not upload_dates:
        return 0
    
    streak = 0
    today = timezone.now().date()
    expected_date = today
    
    for upload_date in upload_dates:
        if upload_date == expected_date:
            streak += 1
            expected_date = expected_date - timedelta(days=1)
        elif upload_date == expected_date + timedelta(days=1):
            continue
        else:
            # Gap found, break the streak
            break
    
    return streak


class NutritionHomeView(generics.GenericAPIView):
    """
    A simple view to confirm the Nutrition app is reachable.
    """
    permission_classes = [IsActiveUser]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='NutritionHomeResponse',
                fields={
                    'message': serializers.CharField(),
                    'total_meals': serializers.IntegerField(),
                    'streak': serializers.IntegerField(),
                    'upload_dates': serializers.ListField(child=serializers.DateField()),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        total_meals = UserUploadedMeal.objects.filter(user=user).count()
        streak = calculate_meal_streak(user)
        
        upload_dates = UserUploadedMeal.objects.filter(user=user).order_by('-created_at').values_list('created_at__date', flat=True).distinct()
        return Response({
            "message": "Welcome to the Nutrition Home!", 
            "total_meals": total_meals,
            "streak": streak,
            "upload_dates": list(upload_dates)
        }, status=200)


class UserUploadedMealCreateView(generics.CreateAPIView):
    """
    API view to handle user uploaded meal images.
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        responses={
            201: inline_serializer(
                name='UserUploadedMealResponse',
                fields={
                    'id': serializers.IntegerField(),
                    'meal_name': serializers.CharField(),
                    'estimated_calories': serializers.FloatField(),
                    'ai_analysis': serializers.CharField(),
                    'macronutrients': serializers.JSONField(),
                    'micronutrients': serializers.JSONField(),
                    'improvements': serializers.CharField(),
                    'created_at': serializers.DateTimeField(),
                    'message': serializers.CharField(),
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        image_file = request.FILES.get('image')

        if not image_file:
            return Response({"error": "No image file provided."}, status=400)

        # Save the uploaded meal instance
        uploaded_meal = UserUploadedMeal.objects.create(
            user=user,
            image=image_file
        )
        
        # Trigger AI analysis (currently runs synchronously since @shared_task is commented out)
        analyze_uploaded_meal(uploaded_meal.id)
        
        # Refresh the object from database to get updated fields after analysis
        uploaded_meal.refresh_from_db()

        return Response({
            "id": uploaded_meal.id,
            "meal_name": uploaded_meal.meal_name,
            "estimated_calories": uploaded_meal.estimated_calories,
            "ai_analysis": uploaded_meal.ai_analysis,
            "macronutrients": uploaded_meal.macronutrients,
            "micronutrients": uploaded_meal.micronutrients,
            "improvements": uploaded_meal.improvements,
            "created_at": uploaded_meal.created_at,
            "message": "Image uploaded and analyzed successfully."
        }, status=201)