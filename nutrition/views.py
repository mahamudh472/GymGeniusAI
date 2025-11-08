from rest_framework import generics, permissions
from rest_framework.response import Response

from accounts.permissions import IsActiveUser
from nutrition.models import UserUploadedMeal
from ai_assistant.utils import analyze_single_meal
from nutrition.tasks import analyze_uploaded_meal

class UserUploadedMealCreateView(generics.CreateAPIView):
    """
    API view to handle user uploaded meal images.
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

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