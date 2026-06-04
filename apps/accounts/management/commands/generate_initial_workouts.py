from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.tasks import generate_initial_workouts_task

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate initial workouts for users who have complete profiles but no workouts yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='Generate workouts for a specific user ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if workouts already exist',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force')

        if user_id:
            # Generate for specific user
            try:
                user = User.objects.get(id=user_id)
                self.generate_for_user(user, force)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {user_id} does not exist')
                )
        else:
            # Generate for all eligible users
            users = User.objects.filter(
                gender__isnull=False,
                age__isnull=False,
                weight_kg__isnull=False,
                height_cm__isnull=False,
                goal__isnull=False,
                activity_level__isnull=False,
            )

            if not force:
                users = users.filter(initial_workouts_generated=False)

            total_users = users.count()
            self.stdout.write(f'Found {total_users} eligible users')

            for user in users:
                self.generate_for_user(user, force)

    def generate_for_user(self, user, force):
        if user.initial_workouts_generated and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Skipping {user.email} - workouts already generated'
                )
            )
            return

        if force:
            # Reset the flag
            user.initial_workouts_generated = False
            user.save(update_fields=['initial_workouts_generated'])
            self.stdout.write(
                self.style.WARNING(f'Forcing regeneration for {user.email}')
            )

        # Trigger the celery task
        result = generate_initial_workouts_task.apply_async(
            args=[str(user.id)],
            countdown=2
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Queued workout generation for {user.email} (Task ID: {result.id})'
            )
        )
