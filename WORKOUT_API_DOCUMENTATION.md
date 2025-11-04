# Workout API Documentation

## Overview

The workout system has been refactored to use **pre-built workouts** instead of AI-generated custom workouts. The AI now recommends and assigns pre-built workouts to users with optional customizations.

## Architecture

### Models

1. **WorkoutCategory**: Categories for organizing workouts (e.g., "Cardio", "Strength Training")
2. **Workout**: Pre-built workout programs with exercises
3. **Exercise**: Individual exercises within a workout
4. **UserWorkout**: Assignment of workouts to users with optional AI customization
5. **UserExerciseCustomization**: Per-user customization of exercise parameters
6. **WorkoutProgress**: Tracking of workout completion and progress

### Key Changes from Old System

| Old Model | New Model | Description |
|-----------|-----------|-------------|
| `Workout.user` | `UserWorkout.user` | Workouts are now shared, not user-specific |
| `Workout.title` | `Workout.name` | Field renamed for consistency |
| `WorkoutRound` | ❌ Removed | Simplified structure - exercises directly in workout |
| `Exercise.round` | `Exercise.workout` | Direct relationship to workout |
| `UserWorkoutProgress` | `WorkoutProgress` | Enhanced with more tracking fields |

## API Endpoints

### Base URL
```
/api/workouts/
```

### 1. Workout Categories

#### List all categories
```http
GET /api/workouts/categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Strength Training",
    "description": "Build muscle and increase strength"
  }
]
```

#### Get category details
```http
GET /api/workouts/categories/{id}/
```

---

### 2. Workouts (Pre-built)

#### List all workouts
```http
GET /api/workouts/workouts/
```

**Query Parameters:**
- `difficulty` - Filter by difficulty (beginner, intermediate, advanced)
- `category` - Filter by category ID
- `search` - Search by name

**Response:**
```json
[
  {
    "id": 1,
    "name": "Full Body Beginner",
    "description": "A complete full-body workout for beginners",
    "difficulty": "beginner",
    "category": {
      "id": 1,
      "name": "Strength Training",
      "description": "Build muscle"
    },
    "estimated_calories": 300,
    "estimated_duration": 45,
    "total_exercises": 8
  }
]
```

#### Get workout details
```http
GET /api/workouts/workouts/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Full Body Beginner",
  "description": "A complete full-body workout",
  "difficulty": "beginner",
  "category": {
    "id": 1,
    "name": "Strength Training",
    "description": "Build muscle"
  },
  "estimated_calories": 300,
  "estimated_duration": 45,
  "video_url": "https://example.com/video.mp4",
  "exercises": [
    {
      "id": 1,
      "name": "Push-ups",
      "description": "Standard push-up exercise",
      "sets": 3,
      "reps": 10,
      "duration_seconds": null,
      "rest_time": 60,
      "order": 1,
      "video_url": "https://example.com/pushup.mp4",
      "tips": "Keep your back straight"
    }
  ],
  "total_exercises": 8,
  "created_at": "2025-11-05T10:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z"
}
```

#### Assign workout to current user
```http
POST /api/workouts/workouts/{id}/assign-to-me/
```

**Request Body:**
```json
{
  "assigned_by_ai": true,
  "custom_notes": "Recommended based on your fitness goals"
}
```

**Response:**
```json
{
  "id": 1,
  "user": 5,
  "user_email": "user@example.com",
  "user_name": "John Doe",
  "workout": { /* full workout object */ },
  "assigned_at": "2025-11-05T10:00:00Z",
  "assigned_by_ai": true,
  "custom_notes": "Recommended based on your fitness goals",
  "is_active": true,
  "exercise_customizations": []
}
```

---

### 3. Exercises

#### List all exercises
```http
GET /api/workouts/exercises/
```

**Query Parameters:**
- `workout` - Filter by workout ID

**Response:**
```json
[
  {
    "id": 1,
    "name": "Push-ups",
    "description": "Standard push-up",
    "sets": 3,
    "reps": 10,
    "duration_seconds": null,
    "rest_time": 60,
    "order": 1,
    "video_url": "https://example.com/video.mp4",
    "tips": "Keep back straight"
  }
]
```

---

### 4. User Workouts (Assigned Workouts)

#### List my assigned workouts
```http
GET /api/workouts/my-workouts/
```

**Query Parameters:**
- `is_active` - Filter by active status (true/false)

**Response:**
```json
[
  {
    "id": 1,
    "user_email": "user@example.com",
    "workout": { /* workout summary */ },
    "assigned_at": "2025-11-05T10:00:00Z",
    "assigned_by_ai": true,
    "is_active": true
  }
]
```

#### Get assigned workout details
```http
GET /api/workouts/my-workouts/{id}/
```

**Response includes full workout details and customizations**

#### Assign a workout to current user
```http
POST /api/workouts/my-workouts/
```

**Request Body:**
```json
{
  "workout_id": 1,
  "assigned_by_ai": false,
  "custom_notes": "Optional notes",
  "is_active": true
}
```

#### Deactivate assigned workout
```http
POST /api/workouts/my-workouts/{id}/deactivate/
```

#### Activate assigned workout
```http
POST /api/workouts/my-workouts/{id}/activate/
```

#### Customize exercise in workout
```http
POST /api/workouts/my-workouts/{id}/customize-exercise/
```

**Request Body:**
```json
{
  "exercise_id": 1,
  "custom_sets": 4,
  "custom_reps": 12,
  "custom_duration_seconds": null,
  "custom_rest_time": 90,
  "notes": "Increase weight gradually"
}
```

**Response:**
```json
{
  "id": 1,
  "exercise": { /* exercise object */ },
  "custom_sets": 4,
  "custom_reps": 12,
  "custom_duration_seconds": null,
  "custom_rest_time": 90,
  "notes": "Increase weight gradually"
}
```

---

### 5. Workout Progress

#### List my workout progress
```http
GET /api/workouts/progress/
```

**Query Parameters:**
- `workout` - Filter by workout ID
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "id": 1,
    "user_workout": { /* user workout summary */ },
    "workout_name": "Full Body Beginner",
    "user_email": "user@example.com",
    "completed_at": "2025-11-05T11:30:00Z",
    "completed_exercises": [1, 2, 3, 4, 5],
    "actual_duration": 50,
    "actual_calories": 320.5,
    "notes": "Great workout!",
    "rating": 5
  }
]
```

#### Log workout completion
```http
POST /api/workouts/progress/
```

**Request Body:**
```json
{
  "user_workout": 1,
  "completed_exercises": [1, 2, 3, 4, 5],
  "actual_duration": 50,
  "actual_calories": 320.5,
  "notes": "Great workout!",
  "rating": 5
}
```

#### Get workout statistics
```http
GET /api/workouts/progress/stats/
```

**Response:**
```json
{
  "total_workouts_completed": 25,
  "total_calories_burned": 7500.0,
  "total_duration_minutes": 1125,
  "average_rating": 4.5
}
```

---

## Typical User Flow

### 1. Browse Available Workouts
```http
GET /api/workouts/workouts/?difficulty=beginner
```

### 2. View Workout Details
```http
GET /api/workouts/workouts/1/
```

### 3. Assign Workout to Self
```http
POST /api/workouts/workouts/1/assign-to-me/
{
  "assigned_by_ai": false,
  "custom_notes": "Starting my fitness journey!"
}
```

### 4. (Optional) Customize Exercises
```http
POST /api/workouts/my-workouts/1/customize-exercise/
{
  "exercise_id": 1,
  "custom_sets": 2,
  "custom_reps": 8,
  "notes": "Starting with lower reps"
}
```

### 5. Complete Workout
```http
POST /api/workouts/progress/
{
  "user_workout": 1,
  "completed_exercises": [1, 2, 3, 4, 5, 6, 7, 8],
  "actual_duration": 45,
  "actual_calories": 300,
  "rating": 5
}
```

### 6. Track Progress
```http
GET /api/workouts/progress/stats/
```

---

## AI Integration Points

The AI can now:

1. **Recommend Workouts**: Analyze user profile and recommend suitable pre-built workouts
2. **Assign Workouts**: Automatically assign workouts to users with `assigned_by_ai=true`
3. **Customize Parameters**: Suggest exercise customizations based on user fitness level
4. **Provide Notes**: Add custom notes with workout assignments explaining the recommendation

Example AI workflow:
```python
# AI recommends a workout
recommended_workout_id = ai_recommend_workout(user_profile)

# AI assigns it to the user
POST /api/workouts/my-workouts/
{
  "workout_id": recommended_workout_id,
  "assigned_by_ai": true,
  "custom_notes": "Based on your goal to build strength and your beginner fitness level, this workout is perfect for you."
}
```

---

## Database Changes Summary

### New Tables
- `user_workouts` - Tracks workout assignments to users
- `user_exercise_customizations` - Stores per-user exercise customizations  
- `workout_progress` - Enhanced progress tracking

### Removed Tables
- `user_workout_progress` (replaced by `workout_progress`)
- `workout_rounds` (simplified structure)

### Modified Tables
- `workouts` - Removed user FK, added timestamps
- `exercises` - Now directly linked to workouts

---

## Migration Notes

The migration (`0003_refactor_workout_models.py`) handles:
- ✅ Data preservation from old fields to new fields
- ✅ Linking exercises to workouts through rounds (before removing rounds)
- ✅ Removing deprecated models safely
- ✅ Adding new models with proper constraints

---

## Authentication

All endpoints require authentication using the `IsActiveUser` permission class.

**Headers:**
```
Authorization: Bearer <your_access_token>
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "exercise_id is required"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Best Practices

1. **Use workout filtering** to help users find suitable workouts quickly
2. **Always include custom_notes** when AI assigns workouts to explain the recommendation
3. **Track progress regularly** to provide better AI recommendations
4. **Use exercise customizations** for gradual progression
5. **Leverage workout statistics** for user motivation and insights

---

## Future Enhancements

Potential improvements to consider:
- Workout difficulty progression tracking
- Social features (share workouts, compete with friends)
- Workout scheduling and reminders
- Exercise video integration
- Custom workout builder (combining existing exercises)
- Workout streaks and achievements
- Advanced analytics and insights
