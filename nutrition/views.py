from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, inline_serializer
from .serializers import UserUploadedMealSerializer, TemporaryMealUploadSerializer
from accounts.permissions import IsActiveUser
from nutrition.models import UserUploadedMeal, TemporaryMealUpload
from ai_assistant.utils import analyze_single_meal
from nutrition.tasks import analyze_uploaded_meal
from django.db.models import Sum
from django.core.files.base import ContentFile
import base64
import os
import shutil


def cleanup_old_temp_uploads():
    """
    Delete temporary meal uploads older than 24 hours.
    This can be called via a cron job or scheduled task.
    """
    threshold_time = timezone.now() - timedelta(hours=24)
    old_uploads = TemporaryMealUpload.objects.filter(created_at__lt=threshold_time)
    count = old_uploads.count()
    old_uploads.delete()  # django-cleanup will handle file deletion
    return count


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
                    'calories_target': serializers.FloatField(),
                    'calories_gain': serializers.FloatField(),
                    'todays_meals': serializers.ListField(child=serializers.JSONField()),
                    'upload_dates': serializers.ListField(child=serializers.DateField()),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            total_meals = UserUploadedMeal.objects.filter(user=user).count()
            streak = calculate_meal_streak(user)
            
            # upload_dates = UserUploadedMeal.objects.filter(user=user).order_by('-created_at').values_list('created_at__date', flat=True).distinct()
            calories_target = user.daily_calorie_target if user.daily_calorie_target else 0
            calories_gain = UserUploadedMeal.objects.filter(
                user=user,
                created_at__date=timezone.now().date()
            ).aggregate(total_calories=Sum('estimated_calories'))['total_calories'] or 0
            todays_meals = UserUploadedMeal.objects.filter(
                user=user,
                created_at__date=timezone.now().date()
            )
            from collections import Counter
            nutrition_totals = Counter()

            for meal in todays_meals:
                if meal.macronutrients:
                    nutrition_totals.update(meal.macronutrients)
                if meal.micronutrients:
                    nutrition_totals.update(meal.micronutrients)
            nutrition_brackdown = convert_nut_data(nutrition_totals)

            return Response({
                "message": "Welcome to the Nutrition Home!", 
                "total_meals": total_meals,
                "streak": streak,
                "calories_target": calories_target,
                "calories_gain": calories_gain,
                "todays_meals": UserUploadedMealSerializer(todays_meals, many=True, context={'request': request}).data,
                "nutrition_brackdown": nutrition_brackdown,
                # "upload_dates": list(upload_dates)
            }, status=200)
        except Exception as e:
            return Response({
                "error": "Failed to retrieve nutrition statistics.",
                "detail": str(e)
            }, status=500)


def convert_nut_data(obj):
    result = []
    for key, value in obj.items():
        result.append({
            'name': "".join(key.split('_')[:-1]).title(),
            'amount': value,
            'unit': key.split('_')[-1]
        })
    return result

class UserUploadedMealCreateView(generics.CreateAPIView):
    """
    API view to handle user uploaded meal images.
    """
    serializer_class = TemporaryMealUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    @extend_schema(
        request=TemporaryMealUploadSerializer,
        responses={
            201: inline_serializer(
                name='UserUploadedMealResponse',
                fields={
                    'temp_upload_id': serializers.IntegerField(),
                    'analysis_data': serializers.JSONField(),
                    'message': serializers.CharField(),
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Debug: Check if image is in request
        if 'image' not in request.FILES:
            return Response({
                "error": "No image file provided.",
                "received_data": list(request.data.keys()),
                "received_files": list(request.FILES.keys())
            }, status=400)
        
        # Use the serializer to validate the uploaded image
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Save the temporary meal upload with the validated data
            temp_upload = serializer.save(user=user)
            
            # Debug: Check if image was saved
            if not temp_upload.image:
                return Response({
                    "error": "Image was not saved resultproperly.",
                    "temp_upload_id": temp_upload.id
                }, status=500)
            
            # Avoid absolute-path access; use storage API for compatibility
            image_name = temp_upload.image.name
            if not image_name or not temp_upload.image.storage.exists(image_name):
                return Response({
                    "error": "Image file does not exist in storage.",
                    "image_name": image_name or "No image name"
                }, status=500)

            # Convert image to base64 for AI analysis
            with temp_upload.image.open('rb') as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            # Perform AI analysis with base64 image
            analysis_data = analyze_single_meal(image_base64)
            temp_upload.analysis_data = analysis_data
            temp_upload.save()

            micronutrients = analysis_data.get('micronutrients', {})
            macronutrients = analysis_data.get('macronutrients', {})

            modified_micronutrients = convert_nut_data(micronutrients)
            modified_macronutrients = convert_nut_data(macronutrients)

            analysis_data['micronutrients'] = modified_micronutrients
            analysis_data['macronutrients'] = modified_macronutrients


            return Response({
                "temp_upload_id": temp_upload.id,
                "analysis_data": analysis_data,
                "message": "Image uploaded and analyzed successfully.",
                "image_path": temp_upload.image.url if temp_upload.image else None
            }, status=201)
        except Exception as e:
            # Clean up temp upload if analysis fails
            if 'temp_upload' in locals():
                temp_upload.delete()
            return Response({
                "error": "Failed to upload and analyze meal image.",
                "detail": str(e)
            }, status=500)


class SaveUserMealUpload(generics.CreateAPIView):
    """
    API view to save the analyzed meal upload to UserUploadedMeal.
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def post(self, request, *args, **kwargs):
        user = request.user
        temp_upload_id = request.data.get('temp_upload_id')

        if not temp_upload_id:
            return Response({"error": "No temporary upload ID provided."}, status=400)
        
        try:
            temp_upload = TemporaryMealUpload.objects.get(id=temp_upload_id, user=user)
            analysis_data = temp_upload.analysis_data 

            # Read from storage API instead of absolute filesystem path
            with temp_upload.image.open('rb') as img_file:
                image_content = img_file.read()
            
            # Get the original filename
            original_filename = os.path.basename(temp_upload.image.name)
            
            # Create UserUploadedMeal with the image content
            user_meal = UserUploadedMeal.objects.create(
                user=user,
                meal_name=analysis_data.get('meal_name', ''),
                estimated_calories=analysis_data.get('estimated_calories', 0),
                ai_analysis=analysis_data.get('overall_health_insight', ''),
                macronutrients=analysis_data.get('macronutrients', {}),
                micronutrients=analysis_data.get('micronutrients', {}),
                improvements=analysis_data.get('improvement_suggestion', '')
            )
            
            # Save the image to the user_meals directory
            user_meal.image.save(original_filename, ContentFile(image_content), save=True)

            # Delete the temporary upload (this will also delete the temp file)
            temp_upload.delete()

            return Response({
                "id": user_meal.id,
                "meal_name": user_meal.meal_name,
                "estimated_calories": user_meal.estimated_calories,
                "message": "User uploaded meal saved successfully."
            }, status=201)
        except TemporaryMealUpload.DoesNotExist:
            return Response({"error": "Temporary upload not found."}, status=404)
        except Exception as e:
            return Response({
                "error": "Failed to save user uploaded meal.",
                "detail": str(e)
            }, status=500)