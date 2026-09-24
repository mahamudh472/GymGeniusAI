from django.utils import timezone
from datetime import timedelta
import json
import calendar
from django.db.models import Sum


def dashboard_callback(request, context):
    """
    Dashboard callback for Unfold admin.
    Gathers key platform statistics and monthly chart data for the admin index page.
    """
    from apps.accounts.models import User, UserSubscription, Coach
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
    current_year = now.year

    # Revenue calculations
    total_revenue_db = UserSubscription.objects.filter(
        payment_status__in=['completed', 'active']
    ).aggregate(total=Sum('plan__price'))['total']
    total_revenue = float(total_revenue_db) if total_revenue_db else 0.0

    revenue_ytd_db = UserSubscription.objects.filter(
        payment_status__in=['completed', 'active'],
        start_date__year=current_year
    ).aggregate(total=Sum('plan__price'))['total']
    revenue_ytd = float(revenue_ytd_db) if revenue_ytd_db else total_revenue

    # Trailing 6 months data for charts
    months_labels = []
    revenue_chart_data = []
    user_growth_chart_data = []

    for i in range(5, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_abbr = calendar.month_abbr[month]
        months_labels.append(month_abbr)

        # Monthly user registrations
        u_count = User.objects.filter(joined_at__year=year, joined_at__month=month).count()
        user_growth_chart_data.append(u_count)

        # Monthly revenue
        rev = UserSubscription.objects.filter(
            start_date__year=year,
            start_date__month=month,
            payment_status__in=['completed', 'active']
        ).aggregate(total=Sum('plan__price'))['total'] or 0
        revenue_chart_data.append(float(rev))

    # Calculate MoM user growth
    current_month_users = user_growth_chart_data[-1]
    last_month_users = user_growth_chart_data[-2] if len(user_growth_chart_data) >= 2 else 0
    if last_month_users > 0:
        user_mom_growth = round(((current_month_users - last_month_users) / last_month_users) * 100)
    else:
        user_mom_growth = 0

    active_subscriptions = UserSubscription.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_coaches = Coach.objects.count()

    context.update(
        {
            # Top KPI metrics
            "total_revenue": total_revenue,
            "revenue_ytd": revenue_ytd,
            "active_subscriptions": active_subscriptions,
            "total_users": total_users,
            "total_coaches": total_coaches,
            "user_mom_growth": user_mom_growth,

            # Chart series (JSON formatted for safe JS consumption)
            "chart_labels_json": json.dumps(months_labels),
            "revenue_chart_json": json.dumps(revenue_chart_data),
            "user_chart_json": json.dumps(user_growth_chart_data),

            # Users & engagement
            "new_users_7d": User.objects.filter(joined_at__gte=last_7_days).count(),
            "new_users_30d": User.objects.filter(joined_at__gte=last_30_days).count(),

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

