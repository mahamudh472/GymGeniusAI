from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.accounts.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Initialize the database with necessary data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database initialization...'))
        
        call_command('init_ranks')
        self.stdout.write(self.style.SUCCESS('Initialized ranks.'))

        call_command("load_exercises")
        self.stdout.write(self.style.SUCCESS('Loaded exercises.'))

        call_command('load_coach_weekday')
        self.stdout.write(self.style.SUCCESS('Loaded coach WeekDay assignments.'))

        # Create subscription plans if they do not exist
        plans = [
            {'name': '12 Months', 'price': 59.99, 'duration_days': 360, "features": ["Body Scan", "Technology save the most", "Money best choice"]},
            {'name': '3 Months', 'price': 29.99, 'duration_days': 90, "features": ["All features included", "Good for trying"]},
            {'name': '1 Month', 'price': 19.99, 'duration_days': 30, "features": ["Full access 30 days", "No long commitment"]},
        ]

        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'price': plan_data['price'],
                    'duration_days': plan_data['duration_days'],
                    'features': plan_data['features'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Ensured subscription plan: {plan_data["name"]}'))
        self.stdout.write(self.style.SUCCESS('Database initialization completed successfully.'))