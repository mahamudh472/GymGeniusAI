"""
Django management command to initialize Pinecone and upload workout dataset.
Run once during initial setup: python manage.py setup_pinecone
"""
from django.core.management.base import BaseCommand
from apps.ai_assistant.utils import initialize_pinecone_index, upload_workout_dataset_to_pinecone


class Command(BaseCommand):
    help = 'Initialize Pinecone index and upload workout dataset (run once during setup)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-path',
            type=str,
            help='Path to gym_workouts_full.csv (optional, defaults to project root)',
        )
        parser.add_argument(
            '--skip-upload',
            action='store_true',
            help='Only initialize index, skip dataset upload',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting Pinecone setup...'))
        
        # Initialize index
        self.stdout.write('Initializing Pinecone index...')
        result = initialize_pinecone_index()
        
        if "error" in result:
            self.stdout.write(self.style.ERROR(f'Error: {result["error"]}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'✓ Index {result["status"]}: {result["index"]}'))
        
        # Upload dataset
        if not options['skip_upload']:
            self.stdout.write('Uploading workout dataset...')
            csv_path = options.get('csv_path')
            upload_result = upload_workout_dataset_to_pinecone(csv_path)
            
            if "error" in upload_result:
                self.stdout.write(self.style.ERROR(f'Error: {upload_result["error"]}'))
                return
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Uploaded {upload_result["chunks_uploaded"]} chunks '
                f'from {upload_result["rows_processed"]} rows'
            ))
        else:
            self.stdout.write(self.style.WARNING('Skipped dataset upload'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Pinecone setup complete!'))
