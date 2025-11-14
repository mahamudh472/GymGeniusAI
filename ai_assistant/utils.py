import json
from openai import OpenAI
# from google.colab import userdata
import re
import base64
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
from django.conf import settings


# Initialize OpenAI client only if API key is available
o = None
if settings.OPENAI_API_KEY:
    o = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_user_image(base64_image):
    """
    Analyzes a user's full-body image and returns a short,
    fitness-relevant description (posture, symmetry, muscle tone, etc.).
    """
    if not settings.OPENAI_API_KEY:
        return "Image analysis unavailable: OpenAI API key not configured."
    
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
        return "Image analysis unavailable due to service error."
    
def analyze_single_meal(base64_image, meal_name="Meal"):
    """
    Analyze a single meal image for its nutritional profile and improvement tips.
    """
    
    if not settings.OPENAI_API_KEY:
        return {
            "meal_name": meal_name,
            "estimated_calories": 0,
            "macronutrients": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "micronutrients": {"vitamin_c_mg": 0, "iron_mg": 0, "calcium_mg": 0},
            "overall_health_insight": "Meal analysis unavailable: OpenAI API key not configured.",
            "improvement_suggestion": "Please configure OpenAI API key to enable meal analysis."
        }

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
        return {
            "meal_name": meal_name,
            "estimated_calories": 0,
            "macronutrients": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "micronutrients": {"vitamin_c_mg": 0, "iron_mg": 0, "calcium_mg": 0},
            "overall_health_insight": "Meal analysis unavailable due to service error.",
            "improvement_suggestion": "Please try again later or contact support.",
            "error": str(e)
        }


def fitness_coach_ai(
    gender,
    age,
    weight_kg,
    height_cm,
    goal,
    activity_level,
    username,
    coach_name,
    current_query,
    image_summary=None,
    conversation_history=None
):
    """
    Main AI chat handler for FitCoach.
    Always returns a clean JSON object with plain-text keys:
      - reply
      - image_summary
    """
    if not settings.OPENAI_API_KEY:
        return {
            "reply": "AI Coach service is temporarily unavailable. OpenAI API key not configured.",
            "image_summary": image_summary or "N/A"
        }
    
    try:
        chatbot_name = "FitCoach"

        system_message = {
            "role": "system",
            "content": f"""
You are "{chatbot_name}", an AI fitness coach that adopts one of four personas.

## Personas
- John — tough love, no excuses, best-results mindset.
- Selma — warm, supportive, emotionally smart.
- Jara — sassy, humorous, and hyper-motivating.
- Chris — professional, focused, efficient.

Active persona: {coach_name}

## User Profile
gender: {gender}
age: {age}
weight_kg: {weight_kg}
height_cm: {height_cm}
goal: {goal}
activity_level: {activity_level}
username: {username}

## Image Analysis Summary
{image_summary or "No image provided."}

## Behavior Guidelines
- Always speak as {coach_name}.
- Be conversational, motivational, and clear.
- Provide structured workout or nutrition guidance.
- Use image_summary for posture/mobility cues.
- Use metric units (kg, cm, km).
- NEVER comment on attractiveness, race, or emotion.
- Respond ONLY in JSON format.

## JSON Response Format
{{
  "reply": "Main assistant message to the user",
  "image_summary": "Shortly analyze each portion of muscle from the image"
}}

Conversation history for context:
{conversation_history}
"""
        }

        user_message = {"role": "user", "content": current_query}

        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            messages=[system_message, user_message],
        )

        raw_output = response.choices[0].message.content.strip()

        # Try to parse JSON safely
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            parsed = {
                "reply": raw_output,
                "image_summary": image_summary or "N/A"
            }

        parsed.setdefault("reply", "I'm ready to help you get fitter!")
        parsed.setdefault("image_summary", image_summary or "N/A")


        def clean_text(text):
            if not isinstance(text, str):
                return text

            text = re.sub(r"\*\*|##|###|\*", "", text)  # remove markdown
            text = re.sub(r"\\u[0-9a-fA-F]{4}", "", text)  # remove unicode escapes
            text = re.sub(r"[\U0001F600-\U0001F64F]", "", text)  # remove emojis
            text = re.sub(r"[\U0001F300-\U0001F5FF]", "", text)
            text = re.sub(r"[\U0001F680-\U0001F6FF]", "", text)
            text = re.sub(r"[\U0001F1E0-\U0001F1FF]", "", text)
            text = re.sub(r"\s*\n\s*", " ", text)  # collapse newlines
            text = re.sub(r"\s{2,}", " ", text)  # remove multiple spaces
            return text.strip()

        parsed["reply"] = clean_text(parsed["reply"])
        parsed["image_summary"] = clean_text(parsed["image_summary"])

        return parsed

    except Exception as e:
        print("Error in fitness_coach_ai:", e)
        return {
            "reply": "Sorry, I'm having trouble processing your request right now. Please try again later.",
            "image_summary": image_summary or "N/A",
            "error": str(e) if settings.DEBUG else "Service temporarily unavailable"
        }


