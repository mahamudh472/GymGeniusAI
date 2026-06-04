from django.core.management.base import BaseCommand
from apps.gamification.models import ActivityType


class Command(BaseCommand):
    help = 'Seeds the CHALLENGE_COMPLETION activity type'

    def handle(self, *args, **options):
        activity, created = ActivityType.objects.get_or_create(
            code='CHALLENGE_COMPLETION',
            defaults={
                'name': 'Challenge Completion',
                'points': 0,  # Points will be determined by the challenge itself
                'description': 'Complete a workout challenge',
                'max_per_day': None,  # No daily limit on challenges
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created CHALLENGE_COMPLETION activity type'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'CHALLENGE_COMPLETION activity type already exists'
                )
            )
