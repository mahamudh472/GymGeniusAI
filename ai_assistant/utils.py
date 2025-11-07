import json
from openai import OpenAI
# from google.colab import userdata
import re
import base64
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
from django.conf import settings


o = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_user_image(base64_image):
    """
    Analyzes a user's full-body image and returns a short,
    fitness-relevant description (posture, symmetry, muscle tone, etc.).
    """
    try:
        response = o.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional fitness assessment assistant. "
                        "Describe the person's physique only in factual, training-relevant terms. "
                        "Mention posture, symmetry, muscle tone, and any visible balance issues. "
                        "Avoid comments on attractiveness, race, or emotion. "
                        "Keep your output concise (1-3 lines)."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this full-body image for training-relevant observations only."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error in analyze_user_image:", e)
        return "Image analysis unavailable."
