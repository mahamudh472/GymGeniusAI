from celery import shared_task
import base64
import logging
from ai_assistant.utils import analyze_user_image
from .models import UserGallery

logger = logging.getLogger(__name__)

@shared_task
def analyze_gallery_image(gallery_id):
    """
    Celery task to analyze a gallery image using AI.
    Runs in the background to avoid blocking the upload request.
    """
    logger.info(f"Starting AI analysis for gallery image ID: {gallery_id}")
    try:
        gallery_image = UserGallery.objects.get(id=gallery_id)
        logger.info(f"Found gallery image: {gallery_image.image.name}")
        
        # Read the image file and convert to base64
        with gallery_image.image.open('rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Image converted to base64, calling AI analysis...")
        # Call the AI analysis function
        analysis_result = analyze_user_image(base64_image)
        logger.info(f"AI analysis completed: {analysis_result}")
        
        # Update the gallery image with AI results
        if isinstance(analysis_result, dict):
            gallery_image.ai_detected = True
            gallery_image.ai_summary = analysis_result.get('summary', 'No summary available.')
            
            # Only update image_type if it's one of the valid choices
            new_image_type = analysis_result.get('image_type', '').lower()
            if new_image_type in ['front', 'side', 'back']:
                gallery_image.image_type = new_image_type
                
            gallery_image.save()
        else:
            gallery_image.ai_detected = False
            gallery_image.ai_summary = f"Analysis failed: {str(analysis_result)}"
            gallery_image.save()
        
        logger.info(f"Successfully updated gallery image {gallery_id} with AI results")
        return f"Successfully analyzed image {gallery_id}"
        
    except UserGallery.DoesNotExist:
        logger.error(f"Gallery image {gallery_id} not found")
        return f"Gallery image {gallery_id} not found"
    except Exception as e:
        logger.error(f"Error analyzing image {gallery_id}: {str(e)}", exc_info=True)
        return f"Error analyzing image {gallery_id}: {str(e)}"
