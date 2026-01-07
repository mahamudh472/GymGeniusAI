from django.core.management.base import BaseCommand
from workouts.models import ExerciseVideo, Exercise
from accounts.models import Coach

class Command(BaseCommand):
    help = 'Load exercise videos into the ExerciseVideo model'

    def handle(self, *args, **options):
        
        video_dir = '/home/mahmud/Downloads/Exercise videos'  # Directory where videos are stored
        created_count = 0
        error_count = 0
        skipped_count = 0

        import os
        for filename in os.listdir(video_dir):
            if filename.endswith('.mp4'):
                exercise_name, coach = os.path.splitext(filename)[0].title().split('(')
                video_path = os.path.join(video_dir, filename)
                try:
                    exercise = Exercise.objects.get(name=exercise_name.strip())
                    coach = Coach.objects.get(name=coach.strip(')'))
                    print(f'Found exercise: {exercise.name} and coach: {coach.name}')
                    # Create ExerciseVideo entry
                    video, created = ExerciseVideo.objects.get_or_create(
                        exercise=exercise,
                        coach=coach
                    )
                    if created or not video.video_file:
                        with open(video_path, 'rb') as f:
                            video.video_file.save(filename, f, save=True)
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Added video for exercise: {exercise_name.strip()}'))
                    else:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f'Video already exists for exercise: {exercise_name.strip()}'))
                
                except Exercise.DoesNotExist:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Exercise not found for video: {exercise_name.strip()}'))
                except Coach.DoesNotExist:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Coach not found for video: {coach.strip(")")}'))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Error processing video {filename}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS('Report:'))
        self.stdout.write(self.style.SUCCESS(f'Total videos added: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Total videos skipped: {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'Total errors: {error_count}'))