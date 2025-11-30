from django.db import transaction, models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from .models import (
    UserRank, PointTransaction, ActivityType, Rank, 
    WeeklyLeaderboard, RankHistory, UserStreak
)

User = get_user_model()


def get_week_start_end(date=None):
    """
    Get the start and end date of the week for a given date.
    Week starts on Monday.
    """
    if date is None:
        date = timezone.now().date()
    
    # Get Monday of the current week
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_or_create_user_rank(user):
    """
    Get or create UserRank for a user.
    If creating, assign the lowest rank.
    """
    try:
        return UserRank.objects.get(user=user)
    except UserRank.DoesNotExist:
        lowest_rank = Rank.objects.order_by('level').first()
        if not lowest_rank:
            raise ValueError("No ranks defined in the system. Please create ranks first.")
        
        user_rank = UserRank.objects.create(
            user=user,
            current_rank=lowest_rank,
            highest_rank_achieved=lowest_rank
        )
        
        # Create streak record
        UserStreak.objects.get_or_create(user=user)
        
        return user_rank


@transaction.atomic
def award_points(user, activity_code: str, metadata: Optional[Dict] = None, 
                 custom_points: Optional[int] = None) -> Tuple[bool, str, int]:
    """
    Award points to a user for completing an activity.
    
    Args:
        user: User object
        activity_code: Code of the activity (from ActivityType model)
        metadata: Optional dict with additional info
        custom_points: Optional custom points (overrides activity default)
    
    Returns:
        Tuple of (success: bool, message: str, points_awarded: int)
    """
    try:
        activity = ActivityType.objects.get(code=activity_code, is_active=True)
    except ActivityType.DoesNotExist:
        return False, f"Activity '{activity_code}' not found or inactive", 0
    
    # Check daily limit
    if activity.max_per_day is not None:
        today = timezone.now().date()
        today_count = PointTransaction.objects.filter(
            user=user,
            activity_type=activity,
            created_at__date=today
        ).count()
        
        if today_count >= activity.max_per_day:
            return False, f"Daily limit reached for {activity.name}", 0
    
    # Determine points to award
    points = custom_points if custom_points is not None else activity.points
    
    # Get or create user rank
    user_rank = get_or_create_user_rank(user)
    
    # Get current week
    week_start, week_end = get_week_start_end()
    
    # Create transaction
    transaction_obj = PointTransaction.objects.create(
        user=user,
        activity_type=activity,
        points=points,
        description=activity.name,
        metadata=metadata or {},
        week_start=week_start
    )
    
    # Update user rank points
    user_rank.total_points += points
    user_rank.weekly_points += points
    user_rank.save(update_fields=['total_points', 'weekly_points'])
    
    return True, f"Awarded {points} points for {activity.name}", points


@transaction.atomic
def process_daily_checkin(user) -> Tuple[bool, str, int]:
    """
    Process daily check-in for a user.
    Updates streak and awards points.
    
    Returns:
        Tuple of (success: bool, message: str, points_awarded: int)
    """
    # Get or create streak
    streak, created = UserStreak.objects.get_or_create(user=user)
    
    # Process check-in
    success, message = streak.check_in()
    
    if not success:
        return False, message, 0
    
    # Award points for check-in
    success, points_msg, points = award_points(
        user, 
        'DAILY_CHECKIN',
        metadata={'streak': streak.current_streak}
    )
    
    # Bonus points for streak milestones
    bonus_points = 0
    if streak.current_streak % 7 == 0:  # Weekly streak bonus
        bonus_success, bonus_msg, bonus_points = award_points(
            user,
            'STREAK_MILESTONE',
            metadata={'milestone': '7_days', 'streak': streak.current_streak},
            custom_points=50
        )
    
    total_points = points + bonus_points
    final_message = f"{message}. Earned {total_points} points!"
    
    return True, final_message, total_points


def get_leaderboard_for_user(user, week_start=None, limit=50):
    """
    Get the leaderboard showing only users in the same rank as the given user.
    
    Args:
        user: User object
        week_start: Optional week start date (defaults to current week)
        limit: Number of users to return
    
    Returns:
        Dict with leaderboard data
    """
    if week_start is None:
        week_start, week_end = get_week_start_end()
    
    user_rank = get_or_create_user_rank(user)
    current_rank = user_rank.current_rank
    
    # Get all users in the same rank, ordered by weekly points
    same_rank_users = UserRank.objects.filter(
        current_rank=current_rank
    ).select_related('user', 'current_rank').order_by('-weekly_points', '-total_points')
    
    # Find user's position
    user_position = None
    leaderboard = []
    
    for idx, ur in enumerate(same_rank_users, start=1):
        entry = {
            'position': idx,
            'user_id': ur.user.id,
            'username': ur.user.profile_name,
            'weekly_points': ur.weekly_points,
            'total_points': ur.total_points,
            'is_current_user': ur.user.id == user.id
        }
        
        if ur.user.id == user.id:
            user_position = idx
        
        leaderboard.append(entry)
    
    # Get users around the current user (context)
    if limit and len(leaderboard) > limit:
        if user_position:
            # Get users around the current user
            start_idx = max(0, user_position - limit // 2)
            end_idx = min(len(leaderboard), start_idx + limit)
            
            # Adjust if we're near the end
            if end_idx - start_idx < limit:
                start_idx = max(0, end_idx - limit)
            
            leaderboard = leaderboard[start_idx:end_idx]
    
    return {
        'rank': current_rank.get_name_display(),
        'rank_level': current_rank.level,
        'rank_color': current_rank.color_code,
        'user_position': user_position,
        'total_users_in_rank': same_rank_users.count(),
        'week_start': week_start.isoformat(),
        'leaderboard': leaderboard[:limit] if limit else leaderboard
    }


def get_user_stats(user):
    """
    Get comprehensive stats for a user.
    """
    user_rank = get_or_create_user_rank(user)
    streak = UserStreak.objects.filter(user=user).first()
    
    # Get recent transactions
    recent_transactions = PointTransaction.objects.filter(
        user=user
    ).select_related('activity_type').order_by('-created_at')[:10]
    
    # Get rank history
    rank_history = RankHistory.objects.filter(
        user=user
    ).select_related('old_rank', 'new_rank').order_by('-changed_at')[:5]
    
    # Calculate position in current rank
    position_in_rank = UserRank.objects.filter(
        current_rank=user_rank.current_rank,
        weekly_points__gte=user_rank.weekly_points
    ).count()
    
    total_in_rank = UserRank.objects.filter(
        current_rank=user_rank.current_rank
    ).count()
    
    return {
        'user': {
            'id': user.id,
            'username': user.username,
        },
        'rank': {
            'name': user_rank.current_rank.get_name_display(),
            'level': user_rank.current_rank.level,
            'color': user_rank.current_rank.color_code,
            'icon': user_rank.current_rank.icon,
        },
        'points': {
            'total': user_rank.total_points,
            'weekly': user_rank.weekly_points,
        },
        'position': {
            'in_rank': position_in_rank,
            'total_in_rank': total_in_rank,
            'percentile': round((1 - (position_in_rank / total_in_rank)) * 100, 2) if total_in_rank > 0 else 0
        },
        'streak': {
            'current': streak.current_streak if streak else 0,
            'longest': streak.longest_streak if streak else 0,
            'total_checkins': streak.total_check_ins if streak else 0,
            'last_checkin': streak.last_check_in.isoformat() if streak and streak.last_check_in else None
        },
        'highest_rank': {
            'name': user_rank.highest_rank_achieved.get_name_display() if user_rank.highest_rank_achieved else None,
            'level': user_rank.highest_rank_achieved.level if user_rank.highest_rank_achieved else None,
        },
        'recent_transactions': [
            {
                'id': t.id,
                'points': t.points,
                'description': t.description,
                'activity': t.activity_type.name if t.activity_type else 'Custom',
                'created_at': t.created_at.isoformat(),
            }
            for t in recent_transactions
        ],
        'rank_history': [
            {
                'old_rank': h.old_rank.get_name_display(),
                'new_rank': h.new_rank.get_name_display(),
                'reason': h.reason,
                'changed_at': h.changed_at.isoformat(),
            }
            for h in rank_history
        ]
    }


@transaction.atomic
def update_weekly_ranks():
    """
    Update ranks for all users based on weekly performance.
    Should be run at the end of each week (e.g., via cron job).
    
    This function:
    1. Creates weekly leaderboard snapshot
    2. Promotes/demotes users based on their performance
    3. Resets weekly points
    """
    week_start, week_end = get_week_start_end()
    
    # Get all ranks ordered by level
    ranks = list(Rank.objects.order_by('level'))
    rank_dict = {rank.id: rank for rank in ranks}
    
    results = {
        'promoted': 0,
        'demoted': 0,
        'maintained': 0,
        'total_processed': 0
    }
    
    # Process each rank
    for rank in ranks:
        # Get all users in this rank
        users_in_rank = list(UserRank.objects.filter(
            current_rank=rank
        ).select_related('user').order_by('-weekly_points', '-total_points'))
        
        total_users = len(users_in_rank)
        
        if total_users == 0:
            continue
        
        # Calculate promotion and demotion cutoffs
        promotion_count = max(1, int(total_users * rank.promotion_threshold / 100))
        demotion_count = max(1, int(total_users * rank.demotion_threshold / 100))
        
        # Get next higher and lower ranks
        next_rank = next((r for r in ranks if r.level == rank.level + 1), None)
        prev_rank = next((r for r in ranks if r.level == rank.level - 1), None)
        
        for idx, user_rank in enumerate(users_in_rank, start=1):
            old_rank = user_rank.current_rank
            new_rank = old_rank
            reason = "Maintained rank"
            
            # Determine if user should be promoted or demoted
            if idx <= promotion_count and next_rank:
                # User is in top X% and there's a higher rank
                new_rank = next_rank
                reason = f"Promoted (Top {rank.promotion_threshold}%)"
                results['promoted'] += 1
            elif idx > total_users - demotion_count and prev_rank:
                # User is in bottom X% and there's a lower rank
                new_rank = prev_rank
                reason = f"Demoted (Bottom {rank.demotion_threshold}%)"
                results['demoted'] += 1
            else:
                results['maintained'] += 1
            
            # Create weekly leaderboard entry
            WeeklyLeaderboard.objects.create(
                user=user_rank.user,
                rank=old_rank,
                week_start=week_start,
                week_end=week_end,
                position=idx,
                position_in_rank=idx,
                total_users_in_rank=total_users,
                weekly_points=user_rank.weekly_points,
                total_points=user_rank.total_points,
                rank_changed=(new_rank != old_rank),
                old_rank=old_rank if new_rank != old_rank else None
            )
            
            # Update rank if changed
            if new_rank != old_rank:
                user_rank.current_rank = new_rank
                
                # Update highest rank achieved
                if new_rank.level > (user_rank.highest_rank_achieved.level if user_rank.highest_rank_achieved else 0):
                    user_rank.highest_rank_achieved = new_rank
                
                user_rank.save(update_fields=['current_rank', 'highest_rank_achieved'])
                
                # Create rank history entry
                RankHistory.objects.create(
                    user=user_rank.user,
                    old_rank=old_rank,
                    new_rank=new_rank,
                    reason=reason,
                    weekly_points=user_rank.weekly_points,
                    position_in_old_rank=idx,
                    week_start=week_start
                )
            
            # Reset weekly points
            user_rank.reset_weekly_points()
            
            results['total_processed'] += 1
    
    return results


def get_available_activities():
    """
    Get all available activities that users can earn points from.
    """
    activities = ActivityType.objects.filter(is_active=True).order_by('name')
    
    return [
        {
            'code': activity.code,
            'name': activity.name,
            'points': activity.points,
            'description': activity.description,
            'max_per_day': activity.max_per_day,
        }
        for activity in activities
    ]


def get_all_ranks():
    """
    Get all ranks in the system.
    """
    ranks = Rank.objects.all().order_by('level')
    
    return [
        {
            'name': rank.get_name_display(),
            'level': rank.level,
            'color': rank.color_code,
            'icon': rank.icon,
            'promotion_threshold': rank.promotion_threshold,
            'demotion_threshold': rank.demotion_threshold,
            'min_points_required': rank.min_points_required,
        }
        for rank in ranks
    ]
