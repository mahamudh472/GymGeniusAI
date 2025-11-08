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
    
def analyze_single_meal(base64_image, meal_name="Meal"):
    """
    Analyze a single meal image for its nutritional profile and improvement tips.
    """

    try:
        system_prompt = (
            "You are a certified AI nutritionist. "
            "Analyze the visible foods in the image and provide:\n"
            "- Estimated calories, protein, carbs, and fat.\n"
            "- Key micronutrients (vitamin C, calcium, iron, etc.).\n"
            "- A short health insight (2-3 sentences) summarizing overall meal quality.\n"
            "- A 2-line improvement suggestion (how to make it healthier or better balanced).\n"
            "Return only valid JSON with this structure:\n\n"
            "{\n"
            "  'meal_name': 'string',\n"
            "  'estimated_calories': int,\n"
            "  'macronutrients': {'protein_g': ..., 'carbs_g': ..., 'fat_g': ...},\n"
            "  'micronutrients': {'vitamin_c_mg': ..., 'iron_mg': ..., 'calcium_mg': ...},\n"
            "  'overall_health_insight': 'string',\n"
            "  'improvement_suggestion': 'string'\n"
            "}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze this {meal_name.lower()} image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]

        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=messages
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {"error": str(e)}
