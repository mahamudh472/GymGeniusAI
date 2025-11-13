# Custom Routine API Documentation

## Overview
The Custom Routine feature allows users to create and manage their own personalized exercise routine. Each user has ONE custom routine where they can add or remove exercises from the exercise library.

## Features
- **One routine per user**: Automatically created on first access
- **Toggle functionality**: Add/remove exercises with a single endpoint
- **Exercise listing**: View all available exercises to add
- **Custom routine exercises**: View all exercises in your custom routine

---

## API Endpoints

### 1. List All Available Exercises
**Endpoint:** `GET /api/workouts/exercises/`

**Description:** Get a list of all available exercises that can be added to the custom routine.

**Query Parameters:**
- `muscle_group` (optional): Filter by muscle group (e.g., "Chest", "Back", "Legs")
- `difficulty` (optional): Filter by difficulty ("beginner", "intermediate", "advanced")
- `category` (optional): Filter by category ID

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/workouts/exercises/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With filters
curl -X GET "http://localhost:8000/api/workouts/exercises/?muscle_group=Chest&difficulty=beginner" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Push-ups",
    "description": "Classic bodyweight chest exercise",
    "video_url": "https://example.com/pushups.mp4",
    "muscle_group": "Chest",
    "category": 2,
    "difficulty": "beginner",
    "default_sets": 3,
    "default_reps": 10,
    "default_duration_seconds": null,
    "default_rest_time": 60,
    "calories_per_rep": 0.5,
    "equipment_needed": "None",
    "tips": "Keep your core tight and back straight",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Bench Press",
    "description": "Compound chest exercise with barbell",
    "video_url": "https://example.com/benchpress.mp4",
    "muscle_group": "Chest",
    "category": 2,
    "difficulty": "intermediate",
    "default_sets": 4,
    "default_reps": 8,
    "default_duration_seconds": null,
    "default_rest_time": 90,
    "calories_per_rep": 1.2,
    "equipment_needed": "Barbell, Bench",
    "tips": "Maintain proper form and control the weight",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 2. Get Custom Routine
**Endpoint:** `GET /api/workouts/custom-routine/`

**Description:** Get the user's custom routine with all added exercises. Creates a new routine if one doesn't exist.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/workouts/custom-routine/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
{
  "id": 1,
  "name": "My Custom Routine",
  "description": "My personalized workout routine",
  "exercise_count": 5,
  "exercises": [
    {
      "id": 1,
      "exercise": 5,
      "exercise_name": "Push-ups",
      "exercise_description": "Classic bodyweight chest exercise",
      "video_url": "https://example.com/pushups.mp4",
      "muscle_group": "Chest",
      "difficulty": "beginner",
      "equipment_needed": "None",
      "sets": 3,
      "reps": 10,
      "duration_seconds": null,
      "rest_time": 60,
      "order": 1,
      "notes": "",
      "added_at": "2024-11-14T10:00:00Z"
    },
    {
      "id": 2,
      "exercise": 12,
      "exercise_name": "Squats",
      "exercise_description": "Compound leg exercise",
      "video_url": "https://example.com/squats.mp4",
      "muscle_group": "Legs",
      "difficulty": "intermediate",
      "equipment_needed": "None",
      "sets": 4,
      "reps": 12,
      "duration_seconds": null,
      "rest_time": 90,
      "order": 2,
      "notes": "",
      "added_at": "2024-11-14T10:05:00Z"
    }
  ],
  "created_at": "2024-11-14T09:00:00Z",
  "updated_at": "2024-11-14T10:05:00Z"
}
```

---

### 3. Update Custom Routine Details
**Endpoint:** `PATCH /api/workouts/custom-routine/`

**Description:** Update the name and/or description of your custom routine.

**Request Body:**
```json
{
  "name": "Morning Strength Routine",
  "description": "My go-to morning workout"
}
```

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/api/workouts/custom-routine/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Strength Routine",
    "description": "My go-to morning workout"
  }'
```

**Example Response:**
```json
{
  "id": 1,
  "name": "Morning Strength Routine",
  "description": "My go-to morning workout",
  "exercise_count": 5,
  "exercises": [...],
  "created_at": "2024-11-14T09:00:00Z",
  "updated_at": "2024-11-14T11:00:00Z"
}
```

---

### 4. Toggle Exercise in Custom Routine
**Endpoint:** `POST /api/workouts/custom-routine/toggle-exercise/`

**Description:** Add or remove an exercise from your custom routine. If the exercise is already in the routine, it will be removed. If not, it will be added.

**Request Body:**
```json
{
  "exercise_id": 5
}
```

**Example Request (Add Exercise):**
```bash
curl -X POST "http://localhost:8000/api/workouts/custom-routine/toggle-exercise/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": 5
  }'
```

**Example Response (Exercise Added):**
```json
{
  "message": "Exercise \"Push-ups\" added to custom routine",
  "action": "added",
  "exercise": {
    "id": 1,
    "exercise": 5,
    "exercise_name": "Push-ups",
    "exercise_description": "Classic bodyweight chest exercise",
    "video_url": "https://example.com/pushups.mp4",
    "muscle_group": "Chest",
    "difficulty": "beginner",
    "equipment_needed": "None",
    "sets": 3,
    "reps": 10,
    "duration_seconds": null,
    "rest_time": 60,
    "order": 1,
    "notes": "",
    "added_at": "2024-11-14T10:00:00Z"
  },
  "custom_routine": {
    "id": 1,
    "name": "My Custom Routine",
    "description": "My personalized workout routine",
    "exercise_count": 1,
    "exercises": [...],
    "created_at": "2024-11-14T09:00:00Z",
    "updated_at": "2024-11-14T10:00:00Z"
  }
}
```

**Example Response (Exercise Removed):**
```json
{
  "message": "Exercise \"Push-ups\" removed from custom routine",
  "action": "removed",
  "exercise": null,
  "custom_routine": {
    "id": 1,
    "name": "My Custom Routine",
    "description": "My personalized workout routine",
    "exercise_count": 0,
    "exercises": [],
    "created_at": "2024-11-14T09:00:00Z",
    "updated_at": "2024-11-14T10:05:00Z"
  }
}
```

---

### 5. List Custom Routine Exercises
**Endpoint:** `GET /api/workouts/custom-routine/exercises/`

**Description:** Get a list of all exercises in your custom routine (without the full routine details).

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/workouts/custom-routine/exercises/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "exercise": 5,
    "exercise_name": "Push-ups",
    "exercise_description": "Classic bodyweight chest exercise",
    "video_url": "https://example.com/pushups.mp4",
    "muscle_group": "Chest",
    "difficulty": "beginner",
    "equipment_needed": "None",
    "sets": 3,
    "reps": 10,
    "duration_seconds": null,
    "rest_time": 60,
    "order": 1,
    "notes": "",
    "added_at": "2024-11-14T10:00:00Z"
  },
  {
    "id": 2,
    "exercise": 12,
    "exercise_name": "Squats",
    "exercise_description": "Compound leg exercise",
    "video_url": "https://example.com/squats.mp4",
    "muscle_group": "Legs",
    "difficulty": "intermediate",
    "equipment_needed": "None",
    "sets": 4,
    "reps": 12,
    "duration_seconds": null,
    "rest_time": 90,
    "order": 2,
    "notes": "",
    "added_at": "2024-11-14T10:05:00Z"
  }
]
```

---

### 6. Complete Custom Routine Exercise
**Endpoint:** `POST /api/workouts/custom-routine/complete-exercise/`

**Description:** Mark a custom routine exercise as completed. This automatically creates an Activity record for tracking your workout history.

**Request Body:**
```json
{
  "custom_routine_exercise_id": 1,
  "actual_sets": 3,
  "actual_reps": 12,
  "actual_duration_seconds": null,
  "duration_minutes": 5,
  "notes": "Felt great! Increased reps.",
  "difficulty_rating": "moderate"
}
```

**Fields:**
- `custom_routine_exercise_id` (required): ID of the custom routine exercise
- `actual_sets` (required): Number of sets completed
- `actual_reps` (optional): Number of reps per set (for rep-based exercises)
- `actual_duration_seconds` (optional): Duration in seconds (for timed exercises)
- `duration_minutes` (required): Total time spent on this exercise
- `notes` (optional): Any notes about the workout
- `difficulty_rating` (optional): "easy", "moderate", or "hard"

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/workouts/custom-routine/complete-exercise/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_routine_exercise_id": 1,
    "actual_sets": 3,
    "actual_reps": 12,
    "duration_minutes": 5,
    "notes": "Felt great!",
    "difficulty_rating": "moderate"
  }'
```

**Example Response:**
```json
{
  "message": "Exercise completed successfully",
  "completion": {
    "id": 1,
    "user": 1,
    "custom_routine_exercise": 1,
    "exercise_name": "Push-ups",
    "actual_sets": 3,
    "actual_reps": 12,
    "actual_duration_seconds": null,
    "duration_minutes": 5,
    "calories_burned": 18.0,
    "notes": "Felt great!",
    "difficulty_rating": "moderate",
    "completed_at": "2024-11-14T15:30:00Z"
  },
  "activity": {
    "id": 10,
    "user": 1,
    "name": "Push-ups",
    "duration": 5,
    "calories": 18.0,
    "created_at": "2024-11-14T15:30:00Z"
  }
}
```

---

### 7. Get Completion History
**Endpoint:** `GET /api/workouts/custom-routine/completion-history/`

**Description:** Get a list of all completed custom routine exercises with optional filtering.

**Query Parameters:**
- `exercise_id` (optional): Filter by specific exercise ID
- `days` (optional): Get completions from the last N days

**Example Request:**
```bash
# Get all completion history
curl -X GET "http://localhost:8000/api/workouts/custom-routine/completion-history/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get completions for a specific exercise
curl -X GET "http://localhost:8000/api/workouts/custom-routine/completion-history/?exercise_id=5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get completions from the last 7 days
curl -X GET "http://localhost:8000/api/workouts/custom-routine/completion-history/?days=7" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 3,
    "user": 1,
    "custom_routine_exercise": 1,
    "exercise_name": "Push-ups",
    "actual_sets": 3,
    "actual_reps": 12,
    "actual_duration_seconds": null,
    "duration_minutes": 5,
    "calories_burned": 18.0,
    "notes": "Felt great!",
    "difficulty_rating": "moderate",
    "completed_at": "2024-11-14T15:30:00Z"
  },
  {
    "id": 2,
    "user": 1,
    "custom_routine_exercise": 2,
    "exercise_name": "Squats",
    "actual_sets": 4,
    "actual_reps": 15,
    "actual_duration_seconds": null,
    "duration_minutes": 8,
    "calories_burned": 30.0,
    "notes": "Legs feeling strong",
    "difficulty_rating": "moderate",
    "completed_at": "2024-11-14T14:00:00Z"
  },
  {
    "id": 1,
    "user": 1,
    "custom_routine_exercise": 1,
    "exercise_name": "Push-ups",
    "actual_sets": 3,
    "actual_reps": 10,
    "actual_duration_seconds": null,
    "duration_minutes": 4,
    "calories_burned": 15.0,
    "notes": "Good warmup",
    "difficulty_rating": "easy",
    "completed_at": "2024-11-13T10:00:00Z"
  }
]
```

---

## Frontend Implementation Guide

### Step 1: Display Exercise List
```javascript
// Fetch all exercises
const fetchExercises = async () => {
  const response = await fetch('http://localhost:8000/api/workouts/exercises/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const exercises = await response.json();
  return exercises;
};
```

### Step 2: Check if Exercise is in Custom Routine
```javascript
// Fetch custom routine to check which exercises are already added
const fetchCustomRoutine = async () => {
  const response = await fetch('http://localhost:8000/api/workouts/custom-routine/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const routine = await response.json();
  
  // Create a Set of exercise IDs for quick lookup
  const addedExerciseIds = new Set(
    routine.exercises.map(ex => ex.exercise)
  );
  
  return { routine, addedExerciseIds };
};
```

### Step 3: Toggle Exercise (Add/Remove)
```javascript
// Toggle exercise in custom routine
const toggleExercise = async (exerciseId) => {
  const response = await fetch(
    'http://localhost:8000/api/workouts/custom-routine/toggle-exercise/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ exercise_id: exerciseId })
    }
  );
  
  const result = await response.json();
  
  // result.action will be either "added" or "removed"
  if (result.action === 'added') {
    console.log('Exercise added!');
  } else {
    console.log('Exercise removed!');
  }
  
  return result;
};
```

### Step 4: Complete Custom Routine Exercise
```javascript
// Complete an exercise and create an Activity
const completeExercise = async (customRoutineExerciseId, performanceData) => {
  const response = await fetch(
    'http://localhost:8000/api/workouts/custom-routine/complete-exercise/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        custom_routine_exercise_id: customRoutineExerciseId,
        actual_sets: performanceData.sets,
        actual_reps: performanceData.reps,
        duration_minutes: performanceData.durationMinutes,
        notes: performanceData.notes,
        difficulty_rating: performanceData.difficulty
      })
    }
  );
  
  const result = await response.json();
  
  // result.activity contains the created Activity record
  // result.completion contains the completion record
  console.log('Exercise completed!', result);
  
  return result;
};
```

### Step 5: Get Completion History
```javascript
// Fetch completion history
const getCompletionHistory = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.exerciseId) {
    params.append('exercise_id', filters.exerciseId);
  }
  
  if (filters.days) {
    params.append('days', filters.days);
  }
  
  const response = await fetch(
    `http://localhost:8000/api/workouts/custom-routine/completion-history/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  const history = await response.json();
  return history;
};

// Get all history
const allHistory = await getCompletionHistory();

// Get last 7 days
const recentHistory = await getCompletionHistory({ days: 7 });

// Get history for specific exercise
const exerciseHistory = await getCompletionHistory({ exerciseId: 5 });
```

### Complete React Component Example
```jsx
import React, { useState, useEffect } from 'react';

const ExerciseLibrary = () => {
  const [exercises, setExercises] = useState([]);
  const [customRoutine, setCustomRoutine] = useState(null);
  const [addedExerciseIds, setAddedExerciseIds] = useState(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Fetch exercises and custom routine in parallel
      const [exercisesRes, routineRes] = await Promise.all([
        fetch('/api/workouts/exercises/', {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        }),
        fetch('/api/workouts/custom-routine/', {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        })
      ]);

      const exercisesData = await exercisesRes.json();
      const routineData = await routineRes.json();

      setExercises(exercisesData);
      setCustomRoutine(routineData);
      
      // Track which exercises are in the routine
      const ids = new Set(routineData.exercises.map(ex => ex.exercise));
      setAddedExerciseIds(ids);
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const handleToggleExercise = async (exerciseId) => {
    try {
      const response = await fetch(
        '/api/workouts/custom-routine/toggle-exercise/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ exercise_id: exerciseId })
        }
      );

      const result = await response.json();

      // Update local state
      if (result.action === 'added') {
        setAddedExerciseIds(prev => new Set([...prev, exerciseId]));
      } else {
        setAddedExerciseIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(exerciseId);
          return newSet;
        });
      }

      // Update custom routine
      setCustomRoutine(result.custom_routine);

      // Show notification
      alert(result.message);
    } catch (error) {
      console.error('Error toggling exercise:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Exercise Library</h1>
      <p>Custom Routine: {customRoutine?.exercise_count} exercises</p>
      
      <div className="exercise-grid">
        {exercises.map(exercise => (
          <div key={exercise.id} className="exercise-card">
            <h3>{exercise.name}</h3>
            <p>{exercise.description}</p>
            <p>Muscle: {exercise.muscle_group}</p>
            <p>Difficulty: {exercise.difficulty}</p>
            
            <button
              onClick={() => handleToggleExercise(exercise.id)}
              className={addedExerciseIds.has(exercise.id) ? 'remove-btn' : 'add-btn'}
            >
              {addedExerciseIds.has(exercise.id) ? 'Remove from Routine' : 'Add to Routine'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExerciseLibrary;
```

---

## Key Features

1. **Automatic Creation**: Custom routine is automatically created when first accessed
2. **One Routine Per User**: Enforced by OneToOneField relationship
3. **Toggle Functionality**: Single endpoint handles both add and remove operations
4. **Order Management**: Exercises maintain order based on when they were added
5. **Default Values**: Exercise parameters default to the exercise's default values
6. **Full Exercise Details**: All exercise information is included in responses

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "exercise_id": ["This field is required."]
}
```

### 404 Not Found
```json
{
  "error": "Exercise not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Database Models

### CustomRoutine Model
- One-to-one relationship with User
- Stores routine name and description
- Timestamps for creation and updates

### CustomRoutineExercise Model
- Links exercises to custom routine
- Allows customization of sets, reps, duration, and rest time
- Maintains exercise order
- Unique constraint prevents duplicate exercises in the same routine

---

## Notes

1. **Duplicate Prevention**: The unique_together constraint ensures an exercise can only be added once to a custom routine
2. **Ordering**: Exercises are automatically ordered based on when they were added (order field + added_at timestamp)
3. **Flexibility**: Users can customize sets, reps, and other parameters for each exercise in their routine
4. **Authentication**: All endpoints require user authentication via JWT token
