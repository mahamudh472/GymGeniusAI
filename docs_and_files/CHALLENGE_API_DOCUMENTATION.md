# Challenge Feature API Documentation

## Overview

The Challenge feature allows users to participate in time-limited workout challenges (daily or weekly) and earn points upon completion. Challenges work similar to regular workout sessions but with time constraints and reward systems integrated with the gamification system.

## Key Features

- **Time-Limited Challenges**: Daily or Weekly challenges with specific start and end times
- **Progress Tracking**: Track completion of individual exercises within a challenge
- **Points Rewards**: Automatically award points when challenges are completed
- **Status Management**: Track challenge status (In Progress, Completed, Failed)
- **Difficulty Levels**: Beginner, Intermediate, Advanced

---

## Models

### Challenge

Represents a workout challenge with exercises and rewards.

**Fields:**
- `name`: Challenge name
- `description`: Challenge description
- `challenge_type`: DAILY or WEEKLY
- `difficulty`: beginner, intermediate, advanced
- `completion_points`: Points awarded upon completion
- `start_date`: When challenge becomes available
- `end_date`: When challenge expires
- `exercises`: JSON array of exercises (similar to UserExercise structure)
- `estimated_duration`: Estimated time in minutes
- `estimated_calories`: Estimated calories to burn
- `is_active`: Whether challenge is active

**Example Exercise Structure:**
```json
[
  {
    "exercise_id": 5,
    "name": "Push-ups",
    "sets": 3,
    "reps": 15,
    "rest_time": 60,
    "notes": "Keep your back straight"
  },
  {
    "exercise_id": 12,
    "name": "Squats",
    "sets": 4,
    "reps": 20,
    "rest_time": 90,
    "notes": "Go down to 90 degrees"
  }
]
```

**Enhanced Exercise Fields:**

When creating challenges, you can include an `exercise_id` field that references an Exercise from the workout system. When `exercise_id` is provided, the API will automatically enrich the response with:
- `description`: Full exercise description
- `video`: Video URL demonstrating the exercise
- `muscle_group`: Target muscle group (e.g., "Chest", "Legs", "Core")
- `difficulty`: Exercise difficulty level
- `equipment_needed`: Required equipment
- `calories_per_rep`: Estimated calories burned per repetition
- `tips`: Exercise tips and best practices

**Minimal Exercise Structure (without exercise_id):**
```json
[
  {
    "name": "Push-ups",
    "sets": 3,
    "reps": 15,
    "rest_time": 60
  }
]
```

### UserChallengeProgress

Tracks a user's progress on a specific challenge.

**Fields:**
- `user`: User participating
- `challenge`: Challenge reference
- `status`: IN_PROGRESS, COMPLETED, FAILED
- `completed_exercises`: Array of completed exercise indices
- `completion_percentage`: Percentage of exercises completed
- `actual_duration`: Actual time taken (minutes)
- `actual_calories`: Actual calories burned
- `points_awarded`: Points received
- `points_claimed`: Whether points have been claimed
- `notes`: User notes
- `rating`: User rating (1-5)
- `difficulty_rating`: User feedback on difficulty

---

## API Endpoints

### 1. List All Challenges

**Endpoint:** `GET /api/gamification/challenges/`

**Description:** Get all active challenges with optional filtering.

**Query Parameters:**
- `challenge_type` (optional): Filter by type (DAILY or WEEKLY)
- `available_only` (optional): Show only currently available challenges (true/false)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": 1,
      "name": "Morning Power Challenge",
      "description": "Start your day with this energizing workout",
      "challenge_type": "DAILY",
      "challenge_type_display": "Daily Challenge",
      "difficulty": "intermediate",
      "difficulty_display": "Intermediate",
      "completion_points": 100,
      "start_date": "2025-11-27T00:00:00Z",
      "end_date": "2025-11-27T23:59:59Z",
      "exercises": [
        {
          "exercise_id": 5,
          "name": "Push-ups",
          "description": "A basic upper body exercise targeting chest, shoulders, and triceps",
          "video": "http://localhost:8000/media/exercise_videos/pushups.mp4",
          "muscle_group": "Chest",
          "difficulty": "beginner",
          "equipment_needed": "None",
          "calories_per_rep": 0.35,
          "tips": "Keep your core tight and back straight throughout the movement",
          "sets": 3,
          "reps": 15,
          "rest_time": 60,
          "notes": "Keep your back straight"
        }
      ],
      "estimated_duration": 30,
      "estimated_calories": 250,
      "is_active": true,
      "is_available": true,
      "time_remaining_seconds": 43200,
      "created_at": "2025-11-27T08:00:00Z"
    }
  ]
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/gamification/challenges/?challenge_type=DAILY&available_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Get Challenge Details

**Endpoint:** `GET /api/gamification/challenges/{id}/`

**Description:** Get detailed information about a specific challenge, including user's progress if started.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Morning Power Challenge",
    "description": "Start your day with this energizing workout",
    "challenge_type": "DAILY",
    "challenge_type_display": "Daily Challenge",
    "difficulty": "intermediate",
    "difficulty_display": "Intermediate",
    "completion_points": 100,
    "start_date": "2025-11-27T00:00:00Z",
    "end_date": "2025-11-27T23:59:59Z",
    "exercises": [
      {
        "exercise_id": 5,
        "name": "Push-ups",
        "description": "A basic upper body exercise targeting chest, shoulders, and triceps",
        "video": "http://localhost:8000/media/exercise_videos/pushups.mp4",
        "muscle_group": "Chest",
        "difficulty": "beginner",
        "equipment_needed": "None",
        "calories_per_rep": 0.35,
        "tips": "Keep your core tight and back straight throughout the movement",
        "sets": 3,
        "reps": 15,
        "rest_time": 60,
        "notes": "Keep your back straight"
      },
      {
        "exercise_id": 12,
        "name": "Squats",
        "description": "Lower body compound exercise targeting quads, glutes, and hamstrings",
        "video": "http://localhost:8000/media/exercise_videos/squats.mp4",
        "muscle_group": "Legs",
        "difficulty": "beginner",
        "equipment_needed": "None",
        "calories_per_rep": 0.45,
        "tips": "Keep your weight on your heels and chest up",
        "sets": 4,
        "reps": 20,
        "rest_time": 90,
        "notes": "Go down to 90 degrees"
      }
    ],
    "estimated_duration": 30,
    "estimated_calories": 250,
    "is_active": true,
    "is_available": true,
    "time_remaining_seconds": 43200,
    "created_at": "2025-11-27T08:00:00Z",
    "user_progress": {
      "id": 5,
      "status": "IN_PROGRESS",
      "completed_exercises": [0],
      "completion_percentage": 50.0,
      "points_awarded": 0,
      "points_claimed": false
    }
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/gamification/challenges/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Start Challenge

**Endpoint:** `POST /api/gamification/challenges/start/`

**Description:** Start participating in a challenge. Creates a progress tracking record.

**Request Body:**
```json
{
  "challenge_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Started challenge: Morning Power Challenge",
  "data": {
    "id": 5,
    "username": "john_doe",
    "challenge": {
      "id": 1,
      "name": "Morning Power Challenge",
      "challenge_type": "DAILY",
      "completion_points": 100,
      "exercises": [...]
    },
    "status": "IN_PROGRESS",
    "status_display": "In Progress",
    "completed_exercises": [],
    "completion_percentage": 0.0,
    "actual_duration": null,
    "actual_calories": null,
    "points_awarded": 0,
    "points_claimed": false,
    "notes": null,
    "rating": null,
    "difficulty_rating": null,
    "started_at": "2025-11-27T10:00:00Z",
    "completed_at": null,
    "updated_at": "2025-11-27T10:00:00Z"
  }
}
```

**Error Response (Already Started):**
```json
{
  "success": false,
  "error": "You have already started this challenge",
  "data": {...}
}
```

**Error Response (Not Available):**
```json
{
  "success": false,
  "error": "This challenge is not currently available"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/gamification/challenges/start/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"challenge_id": 1}'
```

---

### 4. Complete Challenge Exercise

**Endpoint:** `POST /api/gamification/challenges/complete-exercise/`

**Description:** Mark an exercise in a challenge as completed. Automatically awards points when all exercises are completed.

**Request Body:**
```json
{
  "challenge_id": 1,
  "exercise_index": 0,
  "actual_sets": 3,
  "actual_reps": 15,
  "actual_duration": 180,
  "notes": "Felt great, maintained good form"
}
```

**Fields:**
- `challenge_id` (required): ID of the challenge
- `exercise_index` (required): Index of the exercise in the exercises array (0-based)
- `actual_sets` (optional): Number of sets completed
- `actual_reps` (optional): Number of reps completed
- `actual_duration` (optional): Time taken in seconds
- `notes` (optional): User notes about this exercise

**Response (Exercise Completed):**
```json
{
  "success": true,
  "message": "Exercise completed successfully",
  "data": {
    "id": 5,
    "username": "john_doe",
    "challenge": {...},
    "status": "IN_PROGRESS",
    "status_display": "In Progress",
    "completed_exercises": [0],
    "completion_percentage": 50.0,
    "points_awarded": 0,
    "points_claimed": false,
    "started_at": "2025-11-27T10:00:00Z",
    "completed_at": null,
    "updated_at": "2025-11-27T10:15:00Z"
  },
  "challenge_completed": false,
  "points_awarded": 0
}
```

**Response (Challenge Completed):**
```json
{
  "success": true,
  "message": "Exercise completed successfully - Challenge completed!",
  "data": {
    "id": 5,
    "username": "john_doe",
    "challenge": {...},
    "status": "COMPLETED",
    "status_display": "Completed",
    "completed_exercises": [0, 1],
    "completion_percentage": 100.0,
    "actual_duration": 30,
    "actual_calories": 250.0,
    "points_awarded": 100,
    "points_claimed": true,
    "completed_at": "2025-11-27T10:30:00Z",
    "updated_at": "2025-11-27T10:30:00Z"
  },
  "challenge_completed": true,
  "points_awarded": 100,
  "activity_created": true,
  "activity": {
    "id": 42,
    "name": "Challenge: Morning Power Challenge",
    "duration": 30,
    "calories": 250.0,
    "created_at": "2025-11-27T10:30:00Z"
  }
}
```

**Error Response (Already Completed):**
```json
{
  "success": false,
  "error": "Exercise already completed"
}
```

**Error Response (Challenge Expired):**
```json
{
  "success": false,
  "error": "This challenge has expired"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/gamification/challenges/complete-exercise/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": 1,
    "exercise_index": 0,
    "actual_sets": 3,
    "actual_reps": 15,
    "notes": "Great workout!"
  }'
```

---

### 5. Get My Challenge Progress

**Endpoint:** `GET /api/gamification/challenges/my-progress/`

**Description:** Get all challenge progress records for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status (IN_PROGRESS, COMPLETED, FAILED)

**Response:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 5,
      "username": "john_doe",
      "challenge": {
        "id": 1,
        "name": "Morning Power Challenge",
        "challenge_type": "DAILY",
        "completion_points": 100,
        "start_date": "2025-11-27T00:00:00Z",
        "end_date": "2025-11-27T23:59:59Z"
      },
      "status": "COMPLETED",
      "status_display": "Completed",
      "completed_exercises": [0, 1],
      "completion_percentage": 100.0,
      "actual_duration": 30,
      "actual_calories": 250.0,
      "points_awarded": 100,
      "points_claimed": true,
      "rating": 5,
      "difficulty_rating": "just_right",
      "started_at": "2025-11-27T10:00:00Z",
      "completed_at": "2025-11-27T10:30:00Z",
      "updated_at": "2025-11-27T10:30:00Z"
    }
  ]
}
```

**Example Request:**
```bash
# Get all progress
curl -X GET "http://localhost:8000/api/gamification/challenges/my-progress/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only completed challenges
curl -X GET "http://localhost:8000/api/gamification/challenges/my-progress/?status=COMPLETED" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only in-progress challenges
curl -X GET "http://localhost:8000/api/gamification/challenges/my-progress/?status=IN_PROGRESS" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6. Claim Challenge Reward

**Endpoint:** `POST /api/gamification/challenges/claim-reward/`

**Description:** Manually claim reward for a completed challenge (normally auto-claimed).

**Request Body:**
```json
{
  "challenge_progress_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Awarded 100 points for Challenge Completion",
  "points_awarded": 100
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Challenge not completed or points already claimed",
  "points_awarded": 0
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/gamification/challenges/claim-reward/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"challenge_progress_id": 5}'
```

---

## Complete Workflow Example

### Scenario: User completes a daily challenge

```bash
# 1. List available challenges
curl -X GET "http://localhost:8000/api/gamification/challenges/?challenge_type=DAILY&available_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response shows challenge ID 1 is available

# 2. Get challenge details
curl -X GET "http://localhost:8000/api/gamification/challenges/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response shows the challenge has 3 exercises

# 3. Start the challenge
curl -X POST "http://localhost:8000/api/gamification/challenges/start/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"challenge_id": 1}'

# Response: Challenge started successfully

# 4. Complete first exercise (index 0)
curl -X POST "http://localhost:8000/api/gamification/challenges/complete-exercise/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": 1,
    "exercise_index": 0,
    "actual_sets": 3,
    "actual_reps": 15,
    "notes": "Good warmup"
  }'

# Response: Exercise completed, 33.3% complete

# 5. Complete second exercise (index 1)
curl -X POST "http://localhost:8000/api/gamification/challenges/complete-exercise/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": 1,
    "exercise_index": 1,
    "actual_sets": 4,
    "actual_reps": 20
  }'

# Response: Exercise completed, 66.6% complete

# 6. Complete third exercise (index 2)
curl -X POST "http://localhost:8000/api/gamification/challenges/complete-exercise/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": 1,
    "exercise_index": 2,
    "actual_sets": 3,
    "actual_reps": 12
  }'

# Response: Challenge completed! 100 points awarded automatically

# 7. Check my progress and points
curl -X GET "http://localhost:8000/api/gamification/stats/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response shows increased points total

# 8. View my challenge history
curl -X GET "http://localhost:8000/api/gamification/challenges/my-progress/?status=COMPLETED" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Important Notes

1. **Time Constraints**: 
   - Challenges can only be started when they are active (between start_date and end_date)
   - If a challenge expires while in progress, it will be marked as FAILED
   - Check `is_available` field before starting a challenge

2. **Points System**:
   - Points are automatically awarded when a challenge is completed (100% completion)
   - Points are claimed automatically - manual claiming is only for edge cases
   - An activity type called "CHALLENGE_COMPLETION" should exist in ActivityType model

3. **Activity Creation**:
   - When a challenge is completed, an Activity record is automatically created
   - This activity appears in the user's activity history (same as regular workouts)
   - Activity name format: "Challenge: {Challenge Name}"
   - Duration and calories are taken from the challenge's estimated values

4. **Exercise Indexing**:
   - Exercises are stored as a JSON array in the Challenge model
   - When completing exercises, use the array index (0-based)
   - Exercise 0 is the first exercise, Exercise 1 is the second, etc.

5. **One Challenge Per User**:
   - A user can only start each challenge once
   - The system prevents duplicate attempts using unique_together constraint

6. **Status Flow**:
   - IN_PROGRESS → COMPLETED (when all exercises done before expiry)
   - IN_PROGRESS → FAILED (when challenge expires before completion)

---

## Integration with Gamification System

The Challenge feature is fully integrated with the gamification system:

- **Points**: Completing challenges awards points that count towards weekly totals
- **Leaderboard**: Challenge points contribute to leaderboard rankings
- **Rank System**: Challenge points can help users get promoted to higher ranks
- **Activity Tracking**: Challenge completions are logged as point transactions

---

## Admin Setup

To create challenges via Django Admin:

1. Go to Admin Panel → Gamification → Challenges
2. Click "Add Challenge"
3. Fill in:
   - Name, Description, Type, Difficulty
   - Completion Points (reward amount)
   - Start Date, End Date
   - Exercises JSON (follow the structure shown above)
   - Estimated Duration and Calories
4. Mark as Active
5. Save

**Make sure to create the CHALLENGE_COMPLETION activity type in ActivityType model with appropriate points configuration.**

---

## Error Handling

All endpoints follow a consistent error format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200 OK`: Successful request
- `201 Created`: Challenge started successfully
- `400 Bad Request`: Invalid input or business logic error
- `404 Not Found`: Challenge or progress not found
- `401 Unauthorized`: Authentication required

---

## Testing Checklist

- [ ] Create a daily challenge via admin
- [ ] Create a weekly challenge via admin
- [ ] List challenges with filters
- [ ] Start a challenge
- [ ] Try starting same challenge twice (should fail)
- [ ] Complete exercises one by one
- [ ] Verify points awarded upon completion
- [ ] Check challenge in my-progress endpoint
- [ ] Try completing exercise after challenge expires
- [ ] Verify CHALLENGE_COMPLETION activity type exists
- [ ] Check leaderboard after completing challenges
