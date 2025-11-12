# Workout Progress Tracking API

## Endpoint: `/api/workouts/track-progress/`

This endpoint allows users to track their workout progress by marking exercises as completed. When all exercises in a workout are completed, it automatically generates an Activity record.

---

## POST - Mark Exercise as Completed

### URL
```
POST /api/workouts/track-progress/
```

### Authentication
Requires authentication token in header:
```
Authorization: Bearer <your_token>
```

### Request Body

```json
{
    "user_workout_id": 1,
    "user_exercise_id": 5,
    "actual_sets": 3,
    "actual_reps": 12,
    "actual_duration": 180,
    "notes": "Felt good, increased weight"
}
```

#### Parameters:
- `user_workout_id` (integer, required): The ID of the UserWorkout
- `user_exercise_id` (integer, required): The ID of the UserExercise to mark as completed
- `actual_sets` (integer, optional): Actual number of sets completed
- `actual_reps` (integer, optional): Actual number of reps completed
- `actual_duration` (integer, optional): Actual duration in seconds
- `notes` (string, optional): Additional notes about the exercise

### Response (Exercise Completed)

```json
{
    "message": "Exercise marked as completed",
    "workout_progress": {
        "id": 1,
        "user_workout": 1,
        "completed_at": "2025-11-13T10:30:00Z",
        "completed_exercises": [5, 6, 7],
        "completion_percentage": 60.0,
        "actual_duration": 30,
        "actual_calories": 250.0,
        "notes": "Exercise Push-ups: Felt good, increased weight",
        "rating": null,
        "difficulty_rating": null
    },
    "all_completed": false,
    "activity_created": false,
    "activity": null,
    "completion_percentage": 60.0,
    "completed_exercises": 3,
    "total_exercises": 5
}
```

### Response (All Exercises Completed - Activity Created)

```json
{
    "message": "Exercise marked as completed",
    "workout_progress": {
        "id": 1,
        "user_workout": 1,
        "completed_at": "2025-11-13T10:30:00Z",
        "completed_exercises": [5, 6, 7, 8, 9],
        "completion_percentage": 100.0,
        "actual_duration": 45,
        "actual_calories": 400.0,
        "notes": "Full workout completed!",
        "rating": null,
        "difficulty_rating": null
    },
    "all_completed": true,
    "activity_created": true,
    "activity": {
        "id": 10,
        "user": 1,
        "name": "Full Body Workout",
        "duration": 45,
        "calories": 400.0,
        "created_at": "2025-11-13T10:45:00Z"
    },
    "completion_percentage": 100.0,
    "completed_exercises": 5,
    "total_exercises": 5
}
```

---

## GET - Get Current Workout Progress

### URL
```
GET /api/workouts/track-progress/?user_workout_id=1
```

### Authentication
Requires authentication token in header:
```
Authorization: Bearer <your_token>
```

### Query Parameters:
- `user_workout_id` (integer, required): The ID of the UserWorkout to check progress for

### Response (Progress Exists)

```json
{
    "workout_progress": {
        "id": 1,
        "user_workout": 1,
        "completed_at": "2025-11-13T10:30:00Z",
        "completed_exercises": [5, 6, 7],
        "completion_percentage": 60.0,
        "actual_duration": 30,
        "actual_calories": 250.0,
        "notes": null,
        "rating": null,
        "difficulty_rating": null
    },
    "workout_name": "Full Body Workout",
    "total_exercises": 5,
    "completed_exercises": 3,
    "completion_percentage": 60.0,
    "all_completed": false
}
```

### Response (No Progress for Today)

```json
{
    "message": "No progress recorded for today",
    "workout_id": 1,
    "workout_name": "Full Body Workout",
    "total_exercises": 5,
    "completed_exercises": 0,
    "completion_percentage": 0.0
}
```

---

## Error Responses

### 400 Bad Request - Missing Parameters
```json
{
    "user_workout_id": ["This field is required."],
    "user_exercise_id": ["This field is required."]
}
```

### 404 Not Found - Workout Not Found
```json
{
    "detail": "Not found."
}
```

### 404 Not Found - Exercise Not in Workout
```json
{
    "detail": "Not found."
}
```

---

## Usage Flow

1. **Start Workout Session**: Get the workout details with all exercises
   ```
   GET /api/workouts/<workout_id>/
   ```

2. **Mark Exercises as Completed**: As the user completes each exercise, send a POST request
   ```
   POST /api/workouts/track-progress/
   {
       "user_workout_id": 1,
       "user_exercise_id": 5
   }
   ```

3. **Check Progress**: Optionally check the current progress
   ```
   GET /api/workouts/track-progress/?user_workout_id=1
   ```

4. **Complete All Exercises**: When the last exercise is marked complete, an Activity is automatically created

5. **Activity Record**: The Activity will have:
   - Name from the workout name
   - Duration from estimated_duration
   - Calories from estimated_calories
   - Automatic timestamp

---

## Notes

- Progress tracking is per-day. Multiple workout sessions on the same day will update the same progress record.
- The Activity is created only once when all exercises are completed (100% completion).
- Exercise IDs are tracked to prevent duplicate completions.
- The endpoint validates that the workout and exercises belong to the authenticated user.
- Optional fields (actual_sets, actual_reps, actual_duration, notes) can be used to track detailed performance metrics.
