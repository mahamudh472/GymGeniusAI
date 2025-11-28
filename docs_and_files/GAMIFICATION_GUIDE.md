# Gamification System Integration Guide

## Overview
The gamification system is now fully integrated into GymGeniusAI. It provides:
- 6 rank tiers (Bronze, Silver, Gold, Platinum, Diamond, Master)
- Points system with 12 different activity types
- Weekly leaderboards showing only users in the same rank
- Automatic rank promotions/demotions based on weekly performance
- Streak tracking for daily check-ins

## API Endpoints

### Leaderboard & Rankings
- `GET /api/gamification/leaderboard/` - Get current week's leaderboard (same rank only)
- `GET /api/gamification/leaderboard/history/` - Get historical weekly leaderboards
- `GET /api/gamification/ranks/` - List all available ranks
- `GET /api/gamification/user-ranks/me/` - Get current user's rank info

### User Stats
- `GET /api/gamification/stats/` - Get comprehensive user statistics
- `GET /api/gamification/streak/` - Get user's check-in streak info
- `GET /api/gamification/rank-history/` - Get user's rank change history
- `GET /api/gamification/transactions/` - Get user's point transaction history

### Actions
- `POST /api/gamification/checkin/` - Process daily check-in
- `POST /api/gamification/award-points/` - Award points for activities
  ```json
  {
    "activity_code": "COMPLETE_WORKOUT",
    "metadata": {"workout_id": 123},
    "custom_points": null  // optional
  }
  ```

### Activity Types
- `GET /api/gamification/activities/` - List all available activities

## Integration Examples

### 1. Award Points When User Completes a Workout
```python
from gamification.utils import award_points

# In your workout completion view/signal
success, message, points = award_points(
    user=request.user,
    activity_code='COMPLETE_WORKOUT',
    metadata={'workout_id': workout.id, 'duration': workout.duration}
)

if success:
    # Points awarded successfully
    print(f"User earned {points} points!")
```

### 2. Award Points When User Logs a Meal
```python
from gamification.utils import award_points

# In your meal logging view
success, message, points = award_points(
    user=request.user,
    activity_code='LOG_MEAL',
    metadata={
        'meal_id': meal.id,
        'calories': meal.calories
    }
)
```

### 3. Award Points When User Posts Progress Photo
```python
from gamification.utils import award_points

# In your gallery/progress photo view
success, message, points = award_points(
    user=request.user,
    activity_code='PROGRESS_PHOTO',
    metadata={'photo_id': photo.id}
)
```

### 4. Award Points When User Writes Article
```python
from gamification.utils import award_points

# In your article creation view
success, message, points = award_points(
    user=request.user,
    activity_code='WRITE_ARTICLE',
    metadata={'article_id': article.id}
)
```

### 5. Check Daily Calorie/Protein Goals
```python
from gamification.utils import award_points

# Check if user met their calorie goal
if user_calories >= daily_target:
    award_points(
        user=request.user,
        activity_code='CALORIE_GOAL',
        metadata={'calories': user_calories, 'target': daily_target}
    )

# Check if user met their protein goal
if user_protein >= protein_target:
    award_points(
        user=request.user,
        activity_code='PROTEIN_GOAL',
        metadata={'protein': user_protein, 'target': protein_target}
    )
```

### 6. Using Signals to Auto-Award Points
```python
# In your app's signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from gamification.utils import award_points

@receiver(post_save, sender=YourWorkoutModel)
def award_workout_points(sender, instance, created, **kwargs):
    if created and instance.is_completed:
        award_points(
            user=instance.user,
            activity_code='COMPLETE_WORKOUT',
            metadata={'workout_id': instance.id}
        )
```

## Management Commands

### Update Weekly Ranks (Run every Sunday/Monday)
```bash
python manage.py update_weekly_ranks
```

This command:
- Creates weekly leaderboard snapshots
- Promotes top performers to higher ranks
- Demotes low performers to lower ranks
- Resets weekly points to 0
- Records rank history

### Set up Cron Job for Weekly Updates
Add to settings.py:
```python
CRONJOBS = [
    # Run every Monday at 00:00
    ('0 0 * * 1', 'django.core.management.call_command', ['update_weekly_ranks']),
]
```

Then run:
```bash
python manage.py crontab add
```

## Activity Codes Reference

| Code | Activity | Points | Max/Day |
|------|----------|--------|---------|
| `DAILY_CHECKIN` | Daily Check-in | 10 | 1 |
| `COMPLETE_WORKOUT` | Complete Workout | 50 | 3 |
| `LOG_MEAL` | Log Meal | 15 | 5 |
| `CALORIE_GOAL` | Reach Daily Calorie Goal | 25 | 1 |
| `PROTEIN_GOAL` | Reach Daily Protein Goal | 20 | 1 |
| `PROGRESS_PHOTO` | Post Progress Photo | 30 | 1 |
| `WRITE_ARTICLE` | Write Article | 100 | ∞ |
| `ARTICLE_COMMENT` | Comment on Article | 5 | 10 |
| `USE_AI_ASSISTANT` | Use AI Assistant | 5 | 5 |
| `STREAK_MILESTONE` | Streak Milestone | 50 | 1 |
| `UPDATE_PROFILE` | Update Profile | 5 | 1 |
| `WEEKLY_GOAL` | Complete Weekly Goal | 100 | 1 |

## Rank System

| Rank | Level | Promotion % | Demotion % | Min Points |
|------|-------|-------------|------------|------------|
| 🥉 Bronze | 1 | 30% | 0% | 0 |
| 🥈 Silver | 2 | 25% | 20% | 100 |
| 🥇 Gold | 3 | 20% | 20% | 500 |
| 💎 Platinum | 4 | 15% | 20% | 1500 |
| 💠 Diamond | 5 | 10% | 15% | 3000 |
| 👑 Master | 6 | 0% | 10% | 5000 |

- **Promotion %**: Top X% of users in each rank get promoted weekly
- **Demotion %**: Bottom X% of users in each rank get demoted weekly
- **Min Points**: Minimum total lifetime points to maintain rank

## Frontend Integration Tips

### Display User's Current Rank Badge
```javascript
fetch('/api/gamification/user-ranks/me/')
  .then(res => res.json())
  .then(data => {
    const rank = data.data.current_rank;
    console.log(`${rank.icon} ${rank.name_display}`);
    // Apply rank color: rank.color_code
  });
```

### Show Leaderboard for User's Rank
```javascript
fetch('/api/gamification/leaderboard/?limit=50')
  .then(res => res.json())
  .then(data => {
    const { rank, user_position, total_users_in_rank, leaderboard } = data.data;
    // Display leaderboard showing only same-rank users
    // Highlight current user's position
  });
```

### Daily Check-in Button
```javascript
fetch('/api/gamification/checkin/', { method: 'POST' })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log(`${data.message}`);
      console.log(`Earned ${data.points_awarded} points!`);
      console.log(`Current streak: ${data.current_streak} days`);
    }
  });
```

## Database Optimization

The system includes optimized indexes on:
- `UserRank`: `-weekly_points`, `-total_points`, `current_rank`
- `PointTransaction`: `user + created_at`, `week_start + user`
- `WeeklyLeaderboard`: `week_start + rank`, `user + week_start`
- `RankHistory`: `user + changed_at`

## Notes

1. **Leaderboard Privacy**: Users only see others in their same rank/league
2. **Weekly Reset**: Run `update_weekly_ranks` command weekly (automated via cron)
3. **Points are Permanent**: Total points never reset, only weekly points
4. **Automatic UserRank Creation**: Created automatically on first point award
5. **Transaction History**: All points are logged for transparency
6. **Streak Bonuses**: Automatically awarded every 7 days of consecutive check-ins

## Testing

Test the system with:
```bash
# Award some test points
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from gamification.utils import award_points, process_daily_checkin
>>> User = get_user_model()
>>> user = User.objects.first()
>>> process_daily_checkin(user)
>>> award_points(user, 'COMPLETE_WORKOUT')
```

## Next Steps

1. **Integrate in Workout Views**: Add `award_points()` calls when workouts are completed
2. **Integrate in Nutrition Views**: Award points for meal logging and goal achievements
3. **Integrate in Gallery Views**: Award points for progress photos
4. **Integrate in Article Views**: Award points for articles and comments
5. **Add Frontend Components**: Display badges, leaderboards, and user stats
6. **Set up Cron Job**: Automate weekly rank updates
7. **Add Notifications**: Notify users of rank changes and achievements
