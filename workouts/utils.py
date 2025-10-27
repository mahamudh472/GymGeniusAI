import requests
from dotenv import load_dotenv
import os
import json

from accounts.models import User
from .serializers import WorkoutSerializer
from .models import WorkoutCategory, Workout, WorkoutRound, Exercise
from django.db import transaction

# @background(schedule=1)
@transaction.atomic
def create_workouts_from_json(data, user_id=None):
    """
    Creates Workout, WorkoutRound, and Exercise objects from nested JSON.
    
    Args:
        data (list): A list of workouts (parsed JSON).
        user (User): Optional user object to associate with workouts.
    
    Returns:
        list: A list of created Workout objects.
    """
    created_workouts = []
    user = User.objects.get(id=user_id) if user_id else None

    for workout_data in data:
        # --- CATEGORY ---
        category_data = workout_data.get("category")
        category, _ = WorkoutCategory.objects.get_or_create(
            name=category_data["name"],
            defaults={"description": category_data.get("description", "")}
        )

        # --- WORKOUT ---
        workout = Workout.objects.create(
            user=user,
            title=workout_data["title"],
            description=workout_data.get("description"),
            video_url=workout_data.get("video_url"),
            difficulty=workout_data["difficulty"],
            category=category,
            calories_burn=workout_data["calories_burn"],
            duration_minutes=workout_data["duration_minutes"],
        )

        # --- ROUNDS ---
        for round_data in workout_data.get("rounds", []):
            workout_round = WorkoutRound.objects.create(
                workout=workout,
                name=round_data["name"],
                round_order=round_data["round_order"],
            )

            # --- EXERCISES ---
            for exercise_data in round_data.get("exercises", []):
                Exercise.objects.create(
                    round=workout_round,
                    name=exercise_data["name"],
                    reps=exercise_data.get("reps"),
                    sets=exercise_data.get("sets"),
                    rest_seconds=exercise_data.get("rest_seconds"),
                    video_url=exercise_data.get("video_url"),
                    tips=exercise_data.get("tips"),
                )

        created_workouts.append(workout)
        print(f"Created workout: {workout.title}")

    return created_workouts

def save_generated_workouts(goal, duration_minutes, difficulty, user=None):
    """Generate a workout plan and persist it using WorkoutSerializer.
    Returns a list of serialized saved workouts.
    """
    print("Generating workouts...")
    workout_list = generate_workout_plan(goal, duration_minutes, difficulty)
    return create_workouts_from_json(workout_list, user_id=user)

    # if not isinstance(workout_list, list):
    #     raise ValueError("Expected the generated workout plan to be a list.")

    # saved_serialized = []
    # errors = []

    # for workout in workout_list:
    #     serializer = WorkoutSerializer(data=workout)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         saved_serialized.append(serializer.data)
    #     except Exception as exc:
    #         errors.append({"title": workout.get("title"), "error": str(exc)})

    # if errors:
    #     raise Exception(f"Failed to save some workouts: {errors}")

    # return saved_serialized

# Load environment variables
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
model = "deepseek/deepseek-chat-v3.1:free"

def get_ai_response(prompt):
    """Send a chat completion request to OpenRouter."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def generate_workout_plan(goal, duration_minutes, difficulty):
    """Generate structured JSON workout plan."""
    prompt = f"""
You are a fitness assistant. Generate a workout plan **strictly in valid JSON format** only.

Rules:
- Return ONLY valid JSON (no markdown, no explanations).
- Follow this exact structure:
[
    {{
        "rounds": [
            {{
                "name": "Round 1",
                "round_order": 1,
                "exercises": [
                    {{
                        "name": "Butterfly",
                        "reps": 20,
                        "sets": 4,
                        "rest_seconds": 30,
                        "video_url": null,
                        "tips": "this is tips"
                    }}
                ]
            }}
        ],
        "title": "User workout",
        "description": "This is user workouts",
        "video_url": null,
        "difficulty": "{difficulty}",
        "category": {{
            "name": "Upper Body",
            "description": "Upper body exercises."
        }},
        "calories_burn": 1000,
        "duration_minutes": {duration_minutes}
    }}
]

The workout goal is: {goal}.
    """

    raw_response = get_ai_response(prompt)

    # Try to clean and parse the JSON
    try:
        workout_data = json.loads(raw_response)
    except json.JSONDecodeError:
        # If model adds extra text, try to extract JSON portion
        try:
            start = raw_response.find('[')
            end = raw_response.rfind(']') + 1
            workout_data = json.loads(raw_response[start:end])
        except Exception:
            raise ValueError("The AI response was not valid JSON:\n" + raw_response)

    return workout_data


# Example usage
if __name__ == "__main__":
    workout = generate_workout_plan("build muscle", 45, "intermediate")
    with open("workout.json", "w", encoding="utf-8") as f:
        json.dump(workout, f, indent=4, ensure_ascii=False)
    print("Saved workout to workout.json")
