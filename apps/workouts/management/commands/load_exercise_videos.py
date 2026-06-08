from django.core.management.base import BaseCommand
from apps.workouts.models import ExerciseVideo, Exercise
from apps.accounts.models import Coach
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File
import os


class Command(BaseCommand):
    help = "Attach exercise videos; save to storage only if missing"

    def handle(self, *args, **options):
        video_dir = "/mnt/videos"
        prefix = "exercise_videos"

        # Check if source video directory exists
        if not os.path.exists(video_dir):
            self.stdout.write(
                self.style.ERROR(f"Source video directory '{video_dir}' does not exist.")
            )
            return

        created = updated = skipped = uploaded = errors = 0

        for filename in os.listdir(video_dir):
            if not filename.lower().endswith(".mp4"):
                continue

            try:
                name = os.path.splitext(filename)[0]
                exercise_name, coach_name = name.split("(", 1)
                exercise_name = exercise_name.strip().title()
                coach_name = coach_name.strip(")")

                exercise = Exercise.objects.get(name=exercise_name)
                coach = Coach.objects.get(name=coach_name)

                storage_path = f"{prefix}/{filename}"

                # 🔍 Check storage existence
                exists = default_storage.exists(storage_path)

                video, created_flag = ExerciseVideo.objects.get_or_create(
                    exercise=exercise,
                    coach=coach,
                    defaults={"video_file": storage_path},
                )

                if not exists:
                    local_path = os.path.join(video_dir, filename)
                    with open(local_path, "rb") as f:
                        default_storage.save(storage_path, File(f))
                    uploaded += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Saved missing file to storage → {filename}")
                    )

                if created_flag:
                    created += 1
                elif not video.video_file:
                    video.video_file = storage_path
                    video.save(update_fields=["video_file"])
                    updated += 1
                else:
                    skipped += 1

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"Error processing {filename}: {str(e)}")
                )

        self.stdout.write("\n=== REPORT ===")
        self.stdout.write(self.style.SUCCESS(f"Created DB rows: {created}"))
        self.stdout.write(self.style.SUCCESS(f"Saved to storage: {uploaded}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
        self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
