import os
import django
import json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
django.setup()

from workouts.models import Exercise, ExerciseCategory

script_dir = Path(__file__).resolve().parent
json_path = script_dir / "workouts.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    category = ExerciseCategory.objects.get_or_create(
        name=item.get("category", "Uncategorized")
    )[0]
    exercise = Exercise(
        name=item.get("name"),
        description=item.get("description", ""),
        category=category,
        video_url=item.get("video_url", ""),
        muscle_group=item.get("muscle_group", ""),
        difficulty=item.get("difficulty", ""),
        equipment_needed=item.get("equipment", ""),
        tips=item.get("tips", "")
    )
    exercise.save()
    print(f"Saved exercise: {exercise.name}")