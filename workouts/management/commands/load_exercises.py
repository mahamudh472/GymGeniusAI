import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from workouts.models import Exercise, ExerciseCategory


class Command(BaseCommand):
    help = 'Load exercises from gym_workouts_full.csv into the Exercise model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='gym_workouts_full.csv',
            help='Path to the CSV file (default: gym_workouts_full.csv in project root)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing exercises before loading'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        
        # If path is relative, look in project root
        if not os.path.isabs(csv_file):
            csv_file = os.path.join(settings.BASE_DIR, csv_file)
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return
        
        # Clear existing exercises if requested
        if options['clear']:
            count = Exercise.objects.count()
            Exercise.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing exercises'))
        
        # Read and process CSV
        created_count = 0
        updated_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Extract data from CSV
                        muscle_group = row.get('Muscle Group', '').strip()
                        level = row.get('Level', '').strip().lower()
                        equipment_type = row.get('Equipment Type', '').strip()
                        exercise_name = row.get('Exercise Name', '').strip()
                        description = row.get('Description', '').strip()
                        target_muscles = row.get('Target Muscles', '').strip()
                        
                        if not exercise_name:
                            self.stdout.write(self.style.WARNING('Skipping row with empty exercise name'))
                            error_count += 1
                            continue
                        
                        # Map level to difficulty
                        difficulty_mapping = {
                            'beginner': 'beginner',
                            'intermediate': 'intermediate',
                            'advanced': 'advanced'
                        }
                        difficulty = difficulty_mapping.get(level, 'beginner')
                        
                        # Get or create category based on muscle group
                        category = None
                        if muscle_group:
                            category, _ = ExerciseCategory.objects.get_or_create(
                                name=muscle_group,
                                defaults={'description': f'Exercises targeting {muscle_group}'}
                            )
                        
                        # Create or update exercise
                        exercise, created = Exercise.objects.update_or_create(
                            name=exercise_name,
                            defaults={
                                'description': description,
                                'muscle_group': muscle_group,
                                'category': category,
                                'difficulty': difficulty,
                                'equipment_needed': equipment_type,
                                'tips': f'Target Muscles: {target_muscles}' if target_muscles else '',
                                'default_sets': self._get_default_sets(difficulty),
                                'default_reps': self._get_default_reps(difficulty),
                                'default_rest_time': self._get_default_rest_time(difficulty),
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Created: {exercise_name}')
                            )
                        else:
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'↻ Updated: {exercise_name}')
                            )
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Error processing row: {str(e)}')
                        )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to read CSV file: {str(e)}'))
            return
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Import Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count}'))
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  Errors: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Total: {created_count + updated_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))
    
    def _get_default_sets(self, difficulty):
        """Return default sets based on difficulty"""
        return {
            'beginner': 3,
            'intermediate': 4,
            'advanced': 5
        }.get(difficulty, 3)
    
    def _get_default_reps(self, difficulty):
        """Return default reps based on difficulty"""
        return {
            'beginner': 12,
            'intermediate': 10,
            'advanced': 8
        }.get(difficulty, 10)
    
    def _get_default_rest_time(self, difficulty):
        """Return default rest time based on difficulty"""
        return {
            'beginner': 90,
            'intermediate': 60,
            'advanced': 45
        }.get(difficulty, 60)
