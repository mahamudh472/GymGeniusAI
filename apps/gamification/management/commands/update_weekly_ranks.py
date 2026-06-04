from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.gamification.utils import update_weekly_ranks


class Command(BaseCommand):
    help = 'Update weekly ranks based on user performance. Should be run at the end of each week.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.WARNING('Starting weekly rank update process...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE('Running in DRY-RUN mode - no changes will be made')
            )
            return
        
        try:
            results = update_weekly_ranks()
            
            self.stdout.write(
                self.style.SUCCESS('✓ Weekly rank update completed successfully!')
            )
            self.stdout.write('')
            self.stdout.write(f"  Total users processed: {results['total_processed']}")
            self.stdout.write(
                self.style.SUCCESS(f"  ↑ Promoted: {results['promoted']}")
            )
            self.stdout.write(
                self.style.ERROR(f"  ↓ Demoted: {results['demoted']}")
            )
            self.stdout.write(
                self.style.NOTICE(f"  → Maintained: {results['maintained']}")
            )
            self.stdout.write('')
            self.stdout.write(f"Timestamp: {timezone.now()}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error updating weekly ranks: {str(e)}')
            )
            raise
