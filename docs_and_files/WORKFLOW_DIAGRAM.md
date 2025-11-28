# Workout Progress Tracking Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Starts Workout                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GET /api/workouts/<id>/                                             │
│  Returns: Workout with all exercises                                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│             User Completes Each Exercise                             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │  POST /api/workouts/track-progress/       │
         │  {                                         │
         │    "user_workout_id": 1,                  │
         │    "user_exercise_id": 5                  │
         │  }                                        │
         └───────────────┬───────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────────┐
         │  System Checks:                            │
         │  1. Validates workout ownership            │
         │  2. Validates exercise in workout          │
         │  3. Gets/Creates WorkoutProgress           │
         │  4. Adds exercise to completed list        │
         │  5. Calculates completion %                │
         └───────────────┬───────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  All exercises done?  │
              └──────────┬────────────┘
                         │
          ┌──────────────┴──────────────┐
          │ NO                      YES │
          ▼                             ▼
┌─────────────────────┐    ┌─────────────────────────────┐
│  Return Progress    │    │  1. Mark as completed        │
│  Response:          │    │  2. Create Activity:         │
│  - completion: 60%  │    │     - name: workout.name     │
│  - activity: null   │    │     - duration: estimated    │
│                     │    │     - calories: estimated    │
└─────────────────────┘    │  3. Return Progress          │
                           │     Response:                │
                           │     - completion: 100%       │
                           │     - activity: {...}        │
                           └─────────────────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────────┐
                           │  Activity Saved to DB      │
                           │  Available in:             │
                           │  GET /api/workouts/        │
                           │      activities/           │
                           └────────────────────────────┘
```

## Data Flow

### WorkoutProgress Record
```
{
    "id": 1,
    "user_workout": 1,
    "completed_at": "2025-11-13T10:30:00Z",
    "completed_exercises": [5, 6, 7],  ← Exercise IDs added here
    "completion_percentage": 60.0,      ← Calculated automatically
    "actual_duration": null,
    "actual_calories": null
}
```

### When 100% Complete → Activity Created
```
{
    "id": 10,
    "user": 1,
    "name": "Full Body Workout",        ← From workout.name
    "duration": 45,                     ← From workout.estimated_duration
    "calories": 400.0,                  ← From workout.estimated_calories
    "created_at": "2025-11-13T10:45:00Z"
}
```

## Key Points

1. **One Progress Record Per Day**
   - Multiple workout attempts on same day update same record
   - Each day gets a fresh progress record

2. **Exercise Tracking**
   - Exercise IDs stored in `completed_exercises` array
   - Duplicates prevented automatically

3. **Activity Creation**
   - Only happens once at 100% completion
   - Cannot create duplicate activities for same workout session

4. **User Isolation**
   - All operations validate user ownership
   - Users can only track their own workouts

## API Response States

### State 1: In Progress (< 100%)
```json
{
    "all_completed": false,
    "activity_created": false,
    "activity": null,
    "completion_percentage": 60.0
}
```

### State 2: Completed (100%)
```json
{
    "all_completed": true,
    "activity_created": true,
    "activity": {
        "id": 10,
        "name": "Full Body Workout",
        "duration": 45,
        "calories": 400.0
    },
    "completion_percentage": 100.0
}
```

### State 3: Already Completed Today
```json
{
    "all_completed": true,
    "activity_created": false,  ← Activity already exists
    "activity": null,
    "completion_percentage": 100.0
}
```
