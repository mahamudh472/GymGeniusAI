from django.core.management.base import BaseCommand
from django.db import transaction
from apps.gamification.models import ActivityType


class Command(BaseCommand):
    help = 'Initialize default activity types for the gamification system'

    def handle(self, *args, **options):
        self.stdout.write('Creating default activity types...')
        
        activities_data = [
            {
                'name': 'Daily Check-in',
                'code': 'DAILY_CHECKIN',
                'points': 10,
                'description': 'Log in to the app daily',
                'max_per_day': 1,
            },
            {
                'name': 'Complete Workout',
                'code': 'COMPLETE_WORKOUT',
                'points': 50,
                'description': 'Complete a workout session',
                'max_per_day': 3,
            },
            {
                'name': 'Log Meal',
                'code': 'LOG_MEAL',
                'points': 15,
                'description': 'Log a meal with nutrition info',
                'max_per_day': 5,
            },
            {
                'name': 'Reach Daily Calorie Goal',
                'code': 'CALORIE_GOAL',
                'points': 25,
                'description': 'Meet your daily calorie target',
                'max_per_day': 1,
            },
            {
                'name': 'Reach Daily Protein Goal',
                'code': 'PROTEIN_GOAL',
                'points': 20,
                'description': 'Meet your daily protein target',
                'max_per_day': 1,
            },
            {
                'name': 'Post Progress Photo',
                'code': 'PROGRESS_PHOTO',
                'points': 30,
                'description': 'Share a progress photo in gallery',
                'max_per_day': 1,
            },
            {
                'name': 'Write Article',
                'code': 'WRITE_ARTICLE',
                'points': 100,
                'description': 'Write and publish an article',
                'max_per_day': None,
            },
            {
                'name': 'Comment on Article',
                'code': 'ARTICLE_COMMENT',
                'points': 5,
                'description': 'Comment on an article',
                'max_per_day': 10,
            },
            {
                'name': 'Use AI Assistant',
                'code': 'USE_AI_ASSISTANT',
                'points': 5,
                'description': 'Get help from AI assistant',
                'max_per_day': 5,
            },
            {
                'name': 'Streak Milestone',
                'code': 'STREAK_MILESTONE',
                'points': 50,
                'description': 'Reach a streak milestone (7, 14, 30 days)',
                'max_per_day': 1,
            },
            {
                'name': 'Update Profile',
                'code': 'UPDATE_PROFILE',
                'points': 5,
                'description': 'Update your profile information',
                'max_per_day': 1,
            },
            {
                'name': 'Complete Weekly Goal',
                'code': 'WEEKLY_GOAL',
                'points': 100,
                'description': 'Complete all weekly workout goals',
                'max_per_day': 1,
            },
        ]
        
        try:
            with transaction.atomic():
                created_count = 0
                existing_count = 0
                
                for activity_data in activities_data:
                    activity, created = ActivityType.objects.get_or_create(
                        code=activity_data['code'],
                        defaults=activity_data
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created activity: {activity.name} ({activity.points} pts)'
                            )
                        )
                        created_count += 1
                    else:
                        self.stdout.write(
                            self.style.NOTICE(
                                f'• Activity already exists: {activity.name} ({activity.points} pts)'
                            )
                        )
                        existing_count += 1
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully initialized activities! '
                    f'(Created: {created_count}, Existing: {existing_count})'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating activities: {str(e)}')
            )
            raise
