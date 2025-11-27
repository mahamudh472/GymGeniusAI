from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from gamification.models import Challenge


class Command(BaseCommand):
    help = 'Creates sample challenges for testing'

    def handle(self, *args, **options):
        # Create a Daily Challenge
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1) - timedelta(seconds=1)
        
        daily_challenge, created = Challenge.objects.get_or_create(
            name='Daily Power Challenge',
            defaults={
                'description': 'Start your day with this energizing workout! Complete 3 exercises to boost your energy and earn points.',
                'challenge_type': 'DAILY',
                'difficulty': 'intermediate',
                'completion_points': 100,
                'start_date': today_start,
                'end_date': today_end,
                'exercises': [
                    {
                        'name': 'Push-ups',
                        'sets': 3,
                        'reps': 15,
                        'rest_time': 60,
                        'notes': 'Keep your back straight and core engaged'
                    },
                    {
                        'name': 'Squats',
                        'sets': 4,
                        'reps': 20,
                        'rest_time': 90,
                        'notes': 'Go down to 90 degrees, knees behind toes'
                    },
                    {
                        'name': 'Plank Hold',
                        'sets': 3,
                        'duration_seconds': 60,
                        'rest_time': 60,
                        'notes': 'Keep your body in a straight line'
                    }
                ],
                'estimated_duration': 25,
                'estimated_calories': 200,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created Daily Challenge: {daily_challenge.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Daily Challenge already exists: {daily_challenge.name}')
            )
        
        # Create a Weekly Challenge
        week_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())  # Monday
        week_end = week_start + timedelta(days=7) - timedelta(seconds=1)
        
        weekly_challenge, created = Challenge.objects.get_or_create(
            name='Weekly Warrior Challenge',
            defaults={
                'description': 'Push your limits this week! Complete this intense workout and prove you\'re a warrior.',
                'challenge_type': 'WEEKLY',
                'difficulty': 'advanced',
                'completion_points': 500,
                'start_date': week_start,
                'end_date': week_end,
                'exercises': [
                    {
                        'name': 'Burpees',
                        'sets': 5,
                        'reps': 10,
                        'rest_time': 90,
                        'notes': 'Full range of motion, explosive movement'
                    },
                    {
                        'name': 'Mountain Climbers',
                        'sets': 4,
                        'duration_seconds': 45,
                        'rest_time': 60,
                        'notes': 'Fast pace, keep core tight'
                    },
                    {
                        'name': 'Jump Squats',
                        'sets': 4,
                        'reps': 15,
                        'rest_time': 90,
                        'notes': 'Land softly, full squat depth'
                    },
                    {
                        'name': 'Push-up to T',
                        'sets': 3,
                        'reps': 12,
                        'rest_time': 75,
                        'notes': 'Rotate and hold T position for 2 seconds'
                    },
                    {
                        'name': 'High Knees',
                        'sets': 3,
                        'duration_seconds': 60,
                        'rest_time': 60,
                        'notes': 'Bring knees to hip level, fast pace'
                    }
                ],
                'estimated_duration': 45,
                'estimated_calories': 450,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created Weekly Challenge: {weekly_challenge.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Weekly Challenge already exists: {weekly_challenge.name}')
            )
        
        # Create a Beginner Challenge
        beginner_challenge, created = Challenge.objects.get_or_create(
            name='Beginner Fitness Challenge',
            defaults={
                'description': 'Perfect for getting started! A gentle introduction to fitness challenges.',
                'challenge_type': 'DAILY',
                'difficulty': 'beginner',
                'completion_points': 50,
                'start_date': today_start,
                'end_date': today_end,
                'exercises': [
                    {
                        'name': 'Wall Push-ups',
                        'sets': 2,
                        'reps': 10,
                        'rest_time': 60,
                        'notes': 'Stand arms length from wall, lean in and push back'
                    },
                    {
                        'name': 'Chair Squats',
                        'sets': 2,
                        'reps': 12,
                        'rest_time': 60,
                        'notes': 'Sit back to chair, stand up slowly'
                    },
                    {
                        'name': 'March in Place',
                        'sets': 2,
                        'duration_seconds': 30,
                        'rest_time': 45,
                        'notes': 'Lift knees to comfortable height'
                    }
                ],
                'estimated_duration': 15,
                'estimated_calories': 80,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created Beginner Challenge: {beginner_challenge.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Beginner Challenge already exists: {beginner_challenge.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Sample challenges setup completed!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now test the challenge endpoints.')
        )
