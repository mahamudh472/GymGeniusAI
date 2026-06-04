from django.utils import timezone
from datetime import timedelta


def dashboard_callback(request, context):
    """
    Dashboard callback for Unfold admin.
    Gathers key platform statistics for the admin index page.
    """
    from apps.accounts.models import User, UserSubscription
    from apps.workouts.models import Exercise, UserWorkout, WorkoutProgress
    from apps.nutrition.models import Meal, UserUploadedMeal
    from apps.community.models import ForumPost
    from apps.articles.models import Article, WorkoutVideo
    from apps.ai_assistant.models import AIConversation, ConversationMessage
    from apps.gamification.models import (
        Challenge as GamificationChallenge,
        UserChallengeProgress,
    )

    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    context.update(
        {
            # Users
            "total_users": User.objects.count(),
            "new_users_7d": User.objects.filter(joined_at__gte=last_7_days).count(),
            "new_users_30d": User.objects.filter(joined_at__gte=last_30_days).count(),
            "active_subscriptions": UserSubscription.objects.filter(is_active=True).count(),
            # Workouts
            "total_exercises": Exercise.objects.count(),
            "total_user_workouts": UserWorkout.objects.count(),
            "total_completed_workouts": WorkoutProgress.objects.count(),
            # Nutrition
            "total_meals": Meal.objects.count(),
            "total_uploaded_meals": UserUploadedMeal.objects.count(),
            # Community
            "total_forum_posts": ForumPost.objects.count(),
            # Content
            "total_articles": Article.objects.count(),
            "total_workout_videos": WorkoutVideo.objects.count(),
            # AI
            "total_conversations": AIConversation.objects.count(),
            "total_messages": ConversationMessage.objects.count(),
            # Gamification
            "active_challenges": GamificationChallenge.objects.filter(is_active=True).count(),
            "completed_challenges": UserChallengeProgress.objects.filter(status="completed").count(),
        }
    )

    return context
