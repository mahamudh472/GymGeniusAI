from celery import shared_task
import base64
import logging
from ai_assistant.utils import analyze_user_image, analyze_single_meal
from .models import UserUploadedMeal

logger = logging.getLogger(__name__)

# @shared_task
def analyze_uploaded_meal(meal_id):
    """
    Celery task to analyze a user uploaded meal image using AI.
    Runs in the background to avoid blocking the upload request.
    """
    logger.info(f"Starting AI analysis for uploaded meal ID: {meal_id}")
    try:
        uploaded_meal = UserUploadedMeal.objects.get(id=meal_id)
        logger.info(f"Found uploaded meal: {uploaded_meal.image.name}")
        
        # Check if image file exists
        if not uploaded_meal.image:
            logger.error(f"No image file found for meal {meal_id}")
            raise ValueError("No image file found")
        
        # Read the image file and convert to base64
        try:
            with uploaded_meal.image.open('rb') as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
        except Exception as file_error:
            logger.error(f"Error reading image file: {str(file_error)}")
            raise
        
        logger.info(f"Image converted to base64, calling AI analysis...")
        # Call the AI analysis function
        ai_results = analyze_single_meal(base64_image)
        logger.info(f"AI analysis completed: {ai_results}")
        
        # Check if there's an error in AI results
        if "error" in ai_results:
            logger.warning(f"AI analysis returned error: {ai_results.get('error')}")
        
        # Update the uploaded meal with AI results
        uploaded_meal.meal_name = ai_results.get('meal_name', 'Unknown Meal')
        uploaded_meal.estimated_calories = ai_results.get('estimated_calories', 0)
        uploaded_meal.ai_analysis = ai_results.get('overall_health_insight', 'Analysis unavailable')
        uploaded_meal.macronutrients = ai_results.get('macronutrients', {})
        uploaded_meal.micronutrients = ai_results.get('micronutrients', {})
        uploaded_meal.improvements = ai_results.get('improvement_suggestion', 'No suggestions available')
        uploaded_meal.save()
        
        logger.info(f"Successfully updated uploaded meal {meal_id} with AI results")
        return f"Successfully analyzed meal {meal_id}"
        
    except UserUploadedMeal.DoesNotExist:
        logger.error(f"Uploaded meal {meal_id} not found")
        return f"Uploaded meal {meal_id} not found"
    except Exception as e:
        logger.error(f"Error analyzing meal {meal_id}: {str(e)}", exc_info=True)
        # Try to update the meal with error information
        try:
            uploaded_meal = UserUploadedMeal.objects.get(id=meal_id)
            uploaded_meal.meal_name = "Analysis Failed"
            uploaded_meal.ai_analysis = "Unable to analyze meal at this time"
            uploaded_meal.save()
        except:
            pass
        return f"Error analyzing meal {meal_id}: {str(e)}"