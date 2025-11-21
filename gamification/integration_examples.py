"""
Example integrations showing how to award points from other apps.
Copy relevant sections to your actual app views or signals.
"""

# ============================================================================
# WORKOUTS APP INTEGRATION
# ============================================================================

# In workouts/views.py or workouts/signals.py
from gamification.utils import award_points

# Example 1: Award points when workout is completed
def complete_workout_view(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout.is_completed = True
    workout.save()
    
    # Award points
    success, message, points = award_points(
        user=request.user,
        activity_code='COMPLETE_WORKOUT',
        metadata={
            'workout_id': workout.id,
            'duration': workout.duration,
            'exercises_count': workout.exercises.count()
        }
    )
    
    return Response({
        'success': True,
        'workout': WorkoutSerializer(workout).data,
        'points_earned': points,
        'message': message
    })


# Example 2: Using signals for automatic point awarding
from django.db.models.signals import post_save
from django.dispatch import receiver
from workouts.models import WorkoutSession

@receiver(post_save, sender=WorkoutSession)
def award_workout_completion_points(sender, instance, created, **kwargs):
    """Automatically award points when workout is marked complete"""
    if instance.is_completed and not created:
        award_points(
            user=instance.user,
            activity_code='COMPLETE_WORKOUT',
            metadata={'workout_id': instance.id}
        )


# ============================================================================
# NUTRITION APP INTEGRATION
# ============================================================================

# In nutrition/views.py
from gamification.utils import award_points

# Example 3: Award points when meal is logged
class MealLogCreateView(APIView):
    def post(self, request):
        serializer = MealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meal = serializer.save(user=request.user)
        
        # Award points for logging meal
        success, message, points = award_points(
            user=request.user,
            activity_code='LOG_MEAL',
            metadata={
                'meal_id': meal.id,
                'calories': meal.total_calories,
                'meal_type': meal.meal_type
            }
        )
        
        return Response({
            'meal': serializer.data,
            'points_earned': points
        })


# Example 4: Check and award points for daily goals
def check_daily_nutrition_goals(user):
    """Run this at end of day or when user completes all meals"""
    from nutrition.models import DailyNutritionSummary
    
    today = timezone.now().date()
    summary = DailyNutritionSummary.objects.filter(
        user=user, 
        date=today
    ).first()
    
    if not summary:
        return
    
    # Check calorie goal
    if summary.total_calories >= summary.calorie_target:
        award_points(
            user=user,
            activity_code='CALORIE_GOAL',
            metadata={
                'calories': summary.total_calories,
                'target': summary.calorie_target
            }
        )
    
    # Check protein goal
    if summary.total_protein >= summary.protein_target:
        award_points(
            user=user,
            activity_code='PROTEIN_GOAL',
            metadata={
                'protein': summary.total_protein,
                'target': summary.protein_target
            }
        )


# ============================================================================
# GALLERY APP INTEGRATION
# ============================================================================

# In gallery/views.py
from gamification.utils import award_points

# Example 5: Award points for progress photos
class ProgressPhotoUploadView(APIView):
    def post(self, request):
        serializer = PhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(user=request.user)
        
        # Award points
        success, message, points = award_points(
            user=request.user,
            activity_code='PROGRESS_PHOTO',
            metadata={'photo_id': photo.id}
        )
        
        return Response({
            'photo': serializer.data,
            'points_earned': points
        })


# ============================================================================
# ARTICLES APP INTEGRATION
# ============================================================================

# In articles/views.py
from gamification.utils import award_points

# Example 6: Award points for writing article
class ArticleCreateView(generics.CreateAPIView):
    serializer_class = ArticleSerializer
    
    def perform_create(self, serializer):
        article = serializer.save(author=self.request.user)
        
        # Award points
        award_points(
            user=self.request.user,
            activity_code='WRITE_ARTICLE',
            metadata={'article_id': article.id}
        )


# Example 7: Award points for commenting
class CommentCreateView(generics.CreateAPIView):
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        
        # Award points
        award_points(
            user=self.request.user,
            activity_code='ARTICLE_COMMENT',
            metadata={
                'comment_id': comment.id,
                'article_id': comment.article.id
            }
        )


# ============================================================================
# AI ASSISTANT APP INTEGRATION
# ============================================================================

# In ai_assistant/views.py
from gamification.utils import award_points

# Example 8: Award points for using AI assistant
class AIAssistantChatView(APIView):
    def post(self, request):
        # Process AI request
        response = process_ai_chat(request.data['message'])
        
        # Award points
        award_points(
            user=request.user,
            activity_code='USE_AI_ASSISTANT',
            metadata={
                'query_type': request.data.get('query_type'),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return Response({'response': response})


# ============================================================================
# ACCOUNTS APP INTEGRATION
# ============================================================================

# In accounts/views.py
from gamification.utils import award_points, process_daily_checkin

# Example 9: Daily check-in
class DailyCheckInView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        success, message, points = process_daily_checkin(request.user)
        
        return Response({
            'success': success,
            'message': message,
            'points_earned': points
        })


# Example 10: Profile update
class ProfileUpdateView(generics.UpdateAPIView):
    def perform_update(self, serializer):
        serializer.save()
        
        # Award points for profile update
        award_points(
            user=self.request.user,
            activity_code='UPDATE_PROFILE',
            metadata={'updated_fields': list(serializer.validated_data.keys())}
        )


# ============================================================================
# CUSTOM SCHEDULED TASKS
# ============================================================================

# Example 11: Check weekly workout goals (run via cron or celery)
from django.core.management.base import BaseCommand
from gamification.utils import award_points

class Command(BaseCommand):
    help = 'Check and award points for weekly workout goals'
    
    def handle(self, *args, **options):
        from workouts.models import WorkoutSession
        from django.contrib.auth import get_user_model
        from datetime import timedelta
        from django.utils import timezone
        
        User = get_user_model()
        week_start = timezone.now().date() - timedelta(days=7)
        
        for user in User.objects.filter(is_active=True):
            # Check if user completed their weekly workout goal
            workouts_this_week = WorkoutSession.objects.filter(
                user=user,
                is_completed=True,
                completed_at__gte=week_start
            ).count()
            
            # Assuming weekly goal is 4 workouts
            if workouts_this_week >= 4:
                award_points(
                    user=user,
                    activity_code='WEEKLY_GOAL',
                    metadata={
                        'workouts_completed': workouts_this_week,
                        'week_start': week_start.isoformat()
                    }
                )


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

# Example 12: Award points to multiple users
def award_points_to_multiple_users(user_ids, activity_code, metadata=None):
    """Award the same points to multiple users at once"""
    from django.contrib.auth import get_user_model
    from gamification.utils import award_points
    
    User = get_user_model()
    users = User.objects.filter(id__in=user_ids)
    
    results = []
    for user in users:
        success, message, points = award_points(
            user=user,
            activity_code=activity_code,
            metadata=metadata
        )
        results.append({
            'user_id': user.id,
            'success': success,
            'points': points
        })
    
    return results


# ============================================================================
# CUSTOM POINT AWARDS
# ============================================================================

# Example 13: Award custom points for special events
def award_special_event_points(user, event_name, points_amount):
    """Award custom points for special events or achievements"""
    from gamification.utils import award_points
    
    # You can use any activity code or create a generic one
    success, message, earned_points = award_points(
        user=user,
        activity_code='SPECIAL_EVENT',  # Make sure this exists in ActivityType
        metadata={
            'event_name': event_name,
            'description': f'Special event: {event_name}'
        },
        custom_points=points_amount
    )
    
    return success, message, earned_points


# ============================================================================
# FRONTEND INTEGRATION EXAMPLES
# ============================================================================

"""
// React/Vue Example: Display user's rank and points
async function fetchUserGamificationStats() {
    const response = await fetch('/api/gamification/stats/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();
    
    return {
        rank: data.data.rank.name,
        rankColor: data.data.rank.color,
        rankIcon: data.data.rank.icon,
        weeklyPoints: data.data.points.weekly,
        totalPoints: data.data.points.total,
        position: data.data.position.in_rank,
        streak: data.data.streak.current
    };
}

// Display leaderboard
async function fetchLeaderboard() {
    const response = await fetch('/api/gamification/leaderboard/?limit=50');
    const data = await response.json();
    
    return {
        rank: data.data.rank,
        userPosition: data.data.user_position,
        totalUsers: data.data.total_users_in_rank,
        leaderboard: data.data.leaderboard
    };
}

// Daily check-in
async function dailyCheckIn() {
    const response = await fetch('/api/gamification/checkin/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();
    
    if (data.success) {
        console.log(`Earned ${data.points_awarded} points!`);
        console.log(`Streak: ${data.current_streak} days`);
    }
}
"""
