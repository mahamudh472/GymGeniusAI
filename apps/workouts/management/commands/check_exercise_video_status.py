from django.core.management.base import BaseCommand
from apps.accounts.models import Coach
from apps.workouts.models import ExerciseVideo, Exercise

class Command(BaseCommand):
    help = 'Check the status of exercise videos and update their availability.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Provide detailed output for each exercise video status check.'
        )

    def handle(self, *args, **options):
        exercises = Exercise.objects.all()
        missing_videos = 0
        no_missing_videos = 0
        partially_missing_videos = 0

        john = Coach.objects.get(name='John')
        selma = Coach.objects.get(name='Selma')
        jara = Coach.objects.get(name='Jara')
        chris = Coach.objects.get(name='Chris')
        for exercise in exercises:
            current_exercise_missing = 0
            john_video = ExerciseVideo.objects.filter(exercise=exercise, coach=john)
            selma_video = ExerciseVideo.objects.filter(exercise=exercise, coach=selma)
            jara_video = ExerciseVideo.objects.filter(exercise=exercise, coach=jara)
            chris_video = ExerciseVideo.objects.filter(exercise=exercise, coach=chris)

            if john_video.count() == 0:
                current_exercise_missing += 1
                if options['detailed']:
                    self.stdout.write(f'Missing John video for exercise: {exercise.name}')
            if selma_video.count() == 0:
                current_exercise_missing += 1
                if options['detailed']:
                    self.stdout.write(f'Missing Selma video for exercise: {exercise.name}')
            if jara_video.count() == 0:
                current_exercise_missing += 1
                if options['detailed']:
                    self.stdout.write(f'Missing Jara video for exercise: {exercise.name}')
            if chris_video.count() == 0:
                current_exercise_missing += 1
                if options['detailed']:
                    self.stdout.write(f'Missing Chris video for exercise: {exercise.name}')
            missing_videos += current_exercise_missing
            if current_exercise_missing == 0:
                no_missing_videos += 1
            elif current_exercise_missing < 4:
                partially_missing_videos += 1

        self.stdout.write(f'Total missing exercise videos: {missing_videos}')
        self.stdout.write(f'Exercises with no missing videos: {no_missing_videos}')
        self.stdout.write(f'Exercises with partially missing videos: {partially_missing_videos}')
