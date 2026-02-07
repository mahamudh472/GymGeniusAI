from django.core.management.base import BaseCommand
from workouts.models import ExerciseVideo, Exercise
from accounts.models import Coach
from django.conf import settings
import boto3
import os


class Command(BaseCommand):
    help = "Attach exercise videos; upload to S3 only if missing"

    def handle(self, *args, **options):
        video_dir = "/mnt/videos"
        s3_prefix = "exercise_videos"

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        bucket = settings.AWS_STORAGE_BUCKET_NAME

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

                s3_key = f"{s3_prefix}/{filename}"

                # 🔍 Check S3 existence
                exists = True
                try:
                    s3.head_object(Bucket=bucket, Key=s3_key)
                except s3.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] == "404":
                        exists = False
                    else:
                        raise

                video, created_flag = ExerciseVideo.objects.get_or_create(
                    exercise=exercise,
                    coach=coach,
                    defaults={"video_file": s3_key},
                )

                if not exists:
                    local_path = os.path.join(video_dir, filename)
                    s3.upload_file(local_path, bucket, s3_key)
                    uploaded += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Uploaded missing file → {filename}")
                    )

                if created_flag:
                    created += 1
                elif not video.video_file:
                    video.video_file = s3_key
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
        self.stdout.write(self.style.SUCCESS(f"Uploaded to S3: {uploaded}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
        self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
