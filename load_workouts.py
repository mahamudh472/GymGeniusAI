import os
import django
import json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
django.setup()
import csv
from workouts.models import Exercise, ExerciseCategory

script_dir = Path(__file__).resolve().parent
json_path = script_dir / "workouts.json"
csv_path = script_dir / "gym_workouts_full.csv"
# with open(json_path, "r", encoding="utf-8") as f:
#     data = json.load(f)

# for item in data:
#     category = ExerciseCategory.objects.get_or_create(
#         name=item.get("category", "Uncategorized")
#     )[0]
#     exercise = Exercise(
#         name=item.get("name"),
#         description=item.get("description", ""),
#         category=category,
#         video_url=item.get("video_url", ""),
#         muscle_group=item.get("muscle_group", ""),
#         difficulty=item.get("difficulty", ""),
#         equipment_needed=item.get("equipment", ""),
#         tips=item.get("tips", "")
#     )
#     exercise.save()
#     print(f"Saved exercise: {exercise.name}")

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = ExerciseCategory.objects.get_or_create(
            name=row.get("Muscle Group", "Uncategorized")
        )[0]
        exercise, created = Exercise.objects.get_or_create(
            name=row.get("Exercise Name", ""),
            defaults={
            "description": row.get("Description", ""),
            "category": category,
            "video_url": row.get("Video URL", ""),
            "muscle_group": row.get("Target Muscles", ""),
            "difficulty": row.get("Level", ""),
            "equipment_needed": row.get("Equipment Type", ""),
            "tips": row.get("Tips", ""),
            },
        )
        exercise.save()
        print(f"Saved exercise: {exercise.name}")
