# Gamification App

A complete points, ranks, and leaderboard system for GymGeniusAI.

## Features

- ✅ **6-Tier Rank System**: Bronze → Silver → Gold → Platinum → Diamond → Master
- ✅ **Weekly Leaderboards**: Users compete only within their rank/league
- ✅ **Automatic Promotions/Demotions**: Based on weekly performance
- ✅ **12+ Activity Types**: Earn points for various activities
- ✅ **Streak Tracking**: Daily check-in streaks with bonus rewards
- ✅ **Complete History**: Track all point transactions and rank changes
- ✅ **Optimized Queries**: Database indexes for fast leaderboard loading
- ✅ **Reusable Functions**: Easy integration with other apps

## Quick Start

### 1. Initialize Data
```bash
python manage.py init_ranks
python manage.py init_activities
```

### 2. Award Points
```python
from gamification.utils import award_points

success, message, points = award_points(
    user=request.user,
    activity_code='COMPLETE_WORKOUT',
    metadata={'workout_id': 123}
)
```

### 3. Process Daily Check-in
```python
from gamification.utils import process_daily_checkin

success, message, points = process_daily_checkin(request.user)
```

### 4. Get Leaderboard
```python
from gamification.utils import get_leaderboard_for_user

leaderboard = get_leaderboard_for_user(request.user, limit=50)
```

### 5. Get User Stats
```python
from gamification.utils import get_user_stats

stats = get_user_stats(request.user)
```

## API Endpoints

All endpoints are prefixed with `/api/gamification/`

### GET Endpoints
- `/leaderboard/` - Current week's leaderboard
- `/stats/` - User statistics
- `/ranks/` - All ranks
- `/activities/` - All activities
- `/user-ranks/me/` - Current user's rank
- `/transactions/` - Point transaction history
- `/streak/` - User streak info
- `/rank-history/` - Rank change history
- `/leaderboard/history/` - Historical leaderboards

### POST Endpoints
- `/checkin/` - Daily check-in
- `/award-points/` - Award points

## Models

- **Rank**: Defines rank tiers (Bronze, Silver, etc.)
- **ActivityType**: Defines activities that earn points
- **UserRank**: User's current rank and points
- **PointTransaction**: Record of all point awards
- **WeeklyLeaderboard**: Historical weekly rankings
- **RankHistory**: Track rank changes over time
- **UserStreak**: Daily check-in streaks

## Management Commands

```bash
# Update weekly ranks (run every Monday)
python manage.py update_weekly_ranks

# Initialize ranks (one-time)
python manage.py init_ranks

# Initialize activities (one-time)
python manage.py init_activities
```

## Integration

See `integration_examples.py` for detailed integration examples with:
- Workouts app
- Nutrition app
- Gallery app
- Articles app
- AI Assistant app
- Accounts app

## Cron Setup

Add to `settings.py`:
```python
CRONJOBS = [
    ('0 0 * * 1', 'django.core.management.call_command', ['update_weekly_ranks']),
]
```

Run:
```bash
python manage.py crontab add
```

## Documentation

See `GAMIFICATION_GUIDE.md` in the project root for complete documentation.
