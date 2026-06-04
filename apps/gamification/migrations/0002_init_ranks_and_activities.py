from django.db import migrations

def init_ranks_and_activities(apps, schema_editor):
    Rank = apps.get_model('gamification', 'Rank')
    ActivityType = apps.get_model('gamification', 'ActivityType')
    
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
    
    for rank_data in ranks_data:
        Rank.objects.get_or_create(
            name=rank_data['name'],
            defaults=rank_data
        )

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
        {
            'name': 'Complete Challenge',
            'code': 'CHALLENGE_COMPLETION',
            'points': 100,
            'description': 'Awarded for completing a challenge',
            'max_per_day': None,
        },
    ]
    
    for activity_data in activities_data:
        ActivityType.objects.get_or_create(
            code=activity_data['code'],
            defaults=activity_data
        )

def remove_ranks_and_activities(apps, schema_editor):
    Rank = apps.get_model('gamification', 'Rank')
    ActivityType = apps.get_model('gamification', 'ActivityType')
    Rank.objects.all().delete()
    ActivityType.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_ranks_and_activities, remove_ranks_and_activities),
    ]
