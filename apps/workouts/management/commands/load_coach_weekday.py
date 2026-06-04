from django.core.management.base import BaseCommand
from apps.accounts.models import Coach, WeekDay

class Command(BaseCommand):
    help = 'Load coach WeekDay assignments into the WeekDay model'

    def handle(self, *args, **options):
        # Clear existing WeekDay assignments
        WeekDay.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing WeekDay assignments'))

        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        coachs = [
        ["John", "Tough love,no excuses, big results"],
        ["Selma", "Warm, supportive amd emotionally smart"],
        ["Jara", "Sass, humor amd max motivation"],
        ["Chris", "Professional, focused and efficient"]
        ]

        for day in days:
            day, created = WeekDay.objects.get_or_create(name=day)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added WeekDay: {day}'))
        for name, behavior in coachs:
            coach, created = Coach.objects.get_or_create(name=name, behavior=behavior)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added coach: {name} with behavior: {behavior}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded coach WeekDay assignments'))