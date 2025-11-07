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
        logger.info(f"Found gallery image: {gallery_image.image.path}")
        
        # Read the image file and convert to base64
        with open(gallery_image.image.path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Image converted to base64, calling AI analysis...")
        # Call the AI analysis function
        ai_summary = analyze_user_image(base64_image)
        logger.info(f"AI analysis completed: {ai_summary}")
        
        # Update the gallery image with AI results
        gallery_image.ai_detected = True
        gallery_image.ai_summary = ai_summary
        gallery_image.save()
        
        logger.info(f"Successfully updated gallery image {gallery_id} with AI results")
        return f"Successfully analyzed image {gallery_id}"
        
    except UserGallery.DoesNotExist:
        logger.error(f"Gallery image {gallery_id} not found")
        return f"Gallery image {gallery_id} not found"
    except Exception as e:
        logger.error(f"Error analyzing image {gallery_id}: {str(e)}", exc_info=True)
        return f"Error analyzing image {gallery_id}: {str(e)}"
