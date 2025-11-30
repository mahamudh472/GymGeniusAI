# Automatic Workout Generation

This feature automatically generates personalized workouts for users when they complete their profile with all necessary information.

## How It Works

1. **User Profile Completion**: When a user updates their profile with all required fields:
   - Gender
   - Age
   - Weight (kg)
   - Height (cm)
   - Goal
   - Activity Level

2. **Automatic Trigger**: A Django signal (`post_save`) detects the profile completion and triggers a Celery task.

3. **One-Time Execution**: The system tracks whether workouts have been generated using the `initial_workouts_generated` field on the User model. This ensures the task only runs once per user.

4. **Workout Generation**: The Celery task:
   - Generates 3 workout levels (Beginner, Intermediate, Advanced)
   - Uses AI to personalize workouts based on user profile
   - Creates workout records in the database
   - Marks the user as having received initial workouts

## Components

### Models
- **User.initial_workouts_generated**: Boolean field tracking if workouts have been generated

### Tasks
- **generate_initial_workouts_task**: Celery task that generates and saves workouts
  - Location: `accounts/tasks.py`
  - Automatic retry on failure (max 3 retries with exponential backoff)
  - Idempotent (safe to run multiple times)

### Signals
- **check_and_generate_workouts**: Post-save signal on User model
  - Location: `accounts/signals.py`
  - Checks if profile is complete
  - Triggers Celery task with 5-second delay

## Manual Execution

For existing users or administrative purposes, you can manually trigger workout generation:

```bash
# Generate workouts for all eligible users
python manage.py generate_initial_workouts

# Generate workouts for a specific user
python manage.py generate_initial_workouts --user-id <user-uuid>

# Force regeneration even if workouts already exist
python manage.py generate_initial_workouts --force

# Force regeneration for specific user
python manage.py generate_initial_workouts --user-id <user-uuid> --force
```

## Testing

To test the feature:

1. Create a new user or find one without workouts
2. Update their profile with all required fields
3. Check Celery worker logs for task execution
4. Verify workouts were created in the database

```python
from accounts.models import User
from workouts.models import UserWorkout

user = User.objects.get(email='test@example.com')
print(f"Workouts generated: {user.initial_workouts_generated}")
print(f"Workout count: {user.userworkout_set.count()}")
```

## Requirements

- Celery must be running
- OpenAI API key must be configured
- Pinecone vector store must be accessible
- Exercise database must be populated

## Error Handling

- Task retries up to 3 times with exponential backoff
- Logs all errors for debugging
- Gracefully handles missing API keys or database issues
- Returns status information on completion

## Migration

To apply the database changes:

```bash
python manage.py migrate accounts
```
