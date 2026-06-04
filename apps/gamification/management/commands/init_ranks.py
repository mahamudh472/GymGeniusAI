from django.core.management.base import BaseCommand
from django.db import transaction
from apps.gamification.models import Rank


class Command(BaseCommand):
    help = 'Initialize default ranks for the gamification system'

    def handle(self, *args, **options):
        self.stdout.write('Creating default ranks...')
        
        ranks_data = [
            {
                'name': 'BRONZE',
                'level': 1,
                'promotion_threshold': 30.0,
                'demotion_threshold': 0.0,
                'min_points_required': 0,
                'icon': '🥉',
                'color_code': '#CD7F32'
            },
            {
                'name': 'SILVER',
                'level': 2,
                'promotion_threshold': 25.0,
                'demotion_threshold': 20.0,
                'min_points_required': 100,
                'icon': '🥈',
                'color_code': '#C0C0C0'
            },
            {
                'name': 'GOLD',
                'level': 3,
                'promotion_threshold': 20.0,
                'demotion_threshold': 20.0,
                'min_points_required': 500,
                'icon': '🥇',
                'color_code': '#FFD700'
            },
            {
                'name': 'PLATINUM',
                'level': 4,
                'promotion_threshold': 15.0,
                'demotion_threshold': 20.0,
                'min_points_required': 1500,
                'icon': '💎',
                'color_code': '#E5E4E2'
            },
            {
                'name': 'DIAMOND',
                'level': 5,
                'promotion_threshold': 10.0,
                'demotion_threshold': 15.0,
                'min_points_required': 3000,
                'icon': '💠',
                'color_code': '#B9F2FF'
            },
            {
                'name': 'MASTER',
                'level': 6,
                'promotion_threshold': 0.0,
                'demotion_threshold': 10.0,
                'min_points_required': 5000,
                'icon': '👑',
                'color_code': '#9B59B6'
            },
        ]
        
        try:
            with transaction.atomic():
                for rank_data in ranks_data:
                    rank, created = Rank.objects.get_or_create(
                        name=rank_data['name'],
                        defaults=rank_data
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created rank: {rank.get_name_display()} (Level {rank.level})')
                        )
                    else:
                        self.stdout.write(
                            self.style.NOTICE(f'• Rank already exists: {rank.get_name_display()} (Level {rank.level})')
                        )
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(f'Successfully initialized {len(ranks_data)} ranks!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating ranks: {str(e)}')
            )
            raise
