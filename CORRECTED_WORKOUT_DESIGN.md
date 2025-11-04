# Workout System - Corrected Design Documentation

## ✅ Design Philosophy

The system has been corrected to follow this architecture:

**Pre-built Exercises Only** → **AI Creates Dynamic User Workouts** → **Track Progress**

### Key Concept
- ❌ **NOT**: Pre-built workouts that users select
- ✅ **YES**: Pre-built exercises that AI combines into custom workouts for each user

## 📊 Model Structure

### 1. ExerciseCategory
Categories for organizing exercises (e.g., "Cardio", "Strength", "Flexibility")

```python
class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
```

**Purpose**: Organize exercises by type

---

### 2. Exercise (Pre-built Library)
Reusable exercise templates that exist independent of any workout or user.

```python
class Exercise(models.Model):
    # Basic info
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Classification
    muscle_group = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(ExerciseCategory, ...)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Default parameters (AI uses these as starting points)
    default_sets = models.IntegerField(default=3)
    default_reps = models.IntegerField(default=10)
    default_duration_seconds = models.IntegerField(blank=True, null=True)
    default_rest_time = models.IntegerField(default=60)
    
    # Metadata
    calories_per_rep = models.FloatField(default=0.5)
    equipment_needed = models.CharField(max_length=255, blank=True, null=True)
    tips = models.TextField(blank=True, null=True)
```

**Purpose**: 
- Store reusable exercise data
- Provide default parameters for AI to customize
- NOT tied to any specific workout or user

**Example records**:
- Push-ups
- Squats
- Burpees
- Plank
- Running

---

### 3. UserWorkout (Dynamic, User-Specific)
A workout created FOR a specific user (by AI or manually).

```python
class UserWorkout(models.Model):
    user = models.ForeignKey(User, ...)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Metadata
    created_by_ai = models.BooleanField(default=False)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_duration = models.IntegerField(blank=True, null=True)
    estimated_calories = models.IntegerField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Purpose**:
- Represent a complete workout FOR a specific user
- Contains multiple exercises (via UserExercise)
- Each user can have multiple workouts
- AI creates these dynamically

**Example**:
- "John's Monday Full Body Workout"
- "Sarah's Cardio Blast"
- "Mike's Leg Day"

---

### 4. UserExercise (Exercise within a UserWorkout)
Links an Exercise to a UserWorkout with user-specific parameters.

```python
class UserExercise(models.Model):
    user_workout = models.ForeignKey(UserWorkout, related_name='user_exercises', ...)
    exercise = models.ForeignKey(Exercise, ...)
    
    # Customized parameters (can differ from exercise defaults)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    duration_seconds = models.IntegerField(blank=True, null=True)
    rest_time = models.IntegerField(default=60)
    
    # Organization
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
```

**Purpose**:
- Link exercises to user workouts
- Allow AI to customize sets/reps/rest for the specific user
- Define exercise order in the workout
- Add user-specific notes

**Example**:
```
UserWorkout: "John's Monday Workout"
├── UserExercise: Push-ups (3 sets, 15 reps, 60s rest)
├── UserExercise: Squats (4 sets, 12 reps, 90s rest)
└── UserExercise: Plank (3 sets, 45s duration, 60s rest)
```

---

### 5. WorkoutProgress (Completion Tracking)
Tracks when a user completes a workout.

```python
class WorkoutProgress(models.Model):
    user_workout = models.ForeignKey(UserWorkout, related_name='progress_records', ...)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    # Completion tracking
    completed_exercises = models.JSONField(default=list)
    completion_percentage = models.FloatField(default=0.0)
    
    # Actual metrics
    actual_duration = models.IntegerField(blank=True, null=True)
    actual_calories = models.FloatField(blank=True, null=True)
    
    # User feedback
    notes = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    difficulty_rating = models.CharField(max_length=20, choices=...)
```

**Purpose**:
- Track workout completions
- Store actual vs estimated metrics
- Collect user feedback for AI improvement

---

## 🚀 API Endpoints

### Exercise Management

#### List all pre-built exercises
```http
GET /api/workouts/exercises/
Query params: ?difficulty=beginner&muscle_group=chest&search=push
```

```json
[
  {
    "id": 1,
    "name": "Push-ups",
    "muscle_group": "Chest",
    "category_name": "Strength",
    "difficulty": "beginner",
    "default_sets": 3,
    "default_reps": 10,
    "default_rest_time": 60,
    "equipment_needed": "None"
  }
]
```

#### Get exercise details
```http
GET /api/workouts/exercises/1/
```

```json
{
  "id": 1,
  "name": "Push-ups",
  "description": "Classic upper body exercise",
  "video_url": "https://example.com/pushups.mp4",
  "muscle_group": "Chest",
  "category": {"id": 1, "name": "Strength"},
  "difficulty": "beginner",
  "default_sets": 3,
  "default_reps": 10,
  "default_duration_seconds": null,
  "default_rest_time": 60,
  "calories_per_rep": 0.5,
  "equipment_needed": "None",
  "tips": "Keep your back straight...",
  "created_at": "2025-11-05T10:00:00Z"
}
```

---

### User Workout Management

#### List user's workouts
```http
GET /api/workouts/user-workouts/
Query params: ?is_active=true&created_by_ai=true
```

```json
[
  {
    "id": 1,
    "user_email": "john@example.com",
    "name": "Full Body Strength",
    "difficulty": "intermediate",
    "created_by_ai": true,
    "estimated_duration": 45,
    "estimated_calories": 350,
    "is_active": true,
    "total_exercises": 8,
    "created_at": "2025-11-05T10:00:00Z"
  }
]
```

#### Get workout details with exercises
```http
GET /api/workouts/user-workouts/1/
```

```json
{
  "id": 1,
  "user": 5,
  "user_email": "john@example.com",
  "user_name": "John Doe",
  "name": "Full Body Strength",
  "description": "AI-generated workout targeting all major muscle groups",
  "created_by_ai": true,
  "difficulty": "intermediate",
  "estimated_duration": 45,
  "estimated_calories": 350,
  "is_active": true,
  "user_exercises": [
    {
      "id": 1,
      "exercise": {
        "id": 1,
        "name": "Push-ups",
        "video_url": "https://example.com/pushups.mp4",
        ...
      },
      "exercise_name": "Push-ups",
      "exercise_video_url": "https://example.com/pushups.mp4",
      "sets": 3,
      "reps": 15,
      "duration_seconds": null,
      "rest_time": 60,
      "order": 1,
      "notes": "AI: Adjusted reps based on your fitness level"
    },
    {
      "id": 2,
      "exercise": {...},
      "exercise_name": "Squats",
      "sets": 4,
      "reps": 12,
      "rest_time": 90,
      "order": 2,
      "notes": ""
    }
  ],
  "total_exercises": 8,
  "created_at": "2025-11-05T10:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z"
}
```

#### Create a workout (AI or Manual)
```http
POST /api/workouts/user-workouts/
```

```json
{
  "name": "Morning Cardio Blast",
  "description": "Quick cardio session",
  "created_by_ai": true,
  "difficulty": "intermediate",
  "is_active": true,
  "exercises": [
    {
      "exercise_id": 5,
      "sets": 3,
      "reps": 20,
      "rest_time": 30,
      "order": 1,
      "notes": "AI: High intensity recommended"
    },
    {
      "exercise_id": 7,
      "sets": 3,
      "duration_seconds": 60,
      "rest_time": 45,
      "order": 2
    }
  ]
}
```

**Response**: Full workout object with calculated estimates

#### Add exercise to workout
```http
POST /api/workouts/user-workouts/1/add-exercise/
```

```json
{
  "exercise_id": 10,
  "sets": 3,
  "reps": 12,
  "rest_time": 60,
  "order": 9,
  "notes": "Added for extra core work"
}
```

#### Recalculate workout estimates
```http
POST /api/workouts/user-workouts/1/recalculate-estimates/
```

---

### User Exercise Management

#### List exercises in a workout
```http
GET /api/workouts/user-exercises/?workout=1
```

#### Update exercise parameters
```http
PATCH /api/workouts/user-exercises/5/
```

```json
{
  "sets": 4,
  "reps": 15,
  "notes": "Increased intensity"
}
```

#### Remove exercise from workout
```http
DELETE /api/workouts/user-exercises/5/
```

---

### Workout Progress Tracking

#### Log workout completion
```http
POST /api/workouts/progress/
```

```json
{
  "user_workout": 1,
  "completed_exercises": [1, 2, 3, 4, 5, 6, 7, 8],
  "actual_duration": 48,
  "actual_calories": 365.5,
  "rating": 5,
  "difficulty_rating": "just_right",
  "notes": "Great workout! Felt strong."
}
```

#### Get progress history
```http
GET /api/workouts/progress/?start_date=2025-11-01&end_date=2025-11-30
```

#### Get statistics
```http
GET /api/workouts/progress/stats/
```

```json
{
  "total_workouts_completed": 25,
  "total_calories_burned": 8750.5,
  "total_duration_minutes": 1125,
  "average_rating": 4.6,
  "average_completion_percentage": 92.5
}
```

---

## 🤖 AI Integration Guide

### 1. AI Creates a Workout for a User

```python
from workouts.models import Exercise, UserWorkout, UserExercise

def ai_create_workout_for_user(user, fitness_level, goals, duration_minutes):
    """
    AI generates a personalized workout for the user.
    """
    # Step 1: Select appropriate exercises from the library
    exercises = Exercise.objects.filter(
        difficulty=fitness_level,
        muscle_group__in=get_target_muscle_groups(goals)
    )
    
    # Step 2: Create the workout
    workout = UserWorkout.objects.create(
        user=user,
        name=f"AI Workout for {user.first_name}",
        description=f"Personalized {goals} workout",
        created_by_ai=True,
        difficulty=fitness_level,
        is_active=True
    )
    
    # Step 3: Add exercises with AI-customized parameters
    for idx, exercise in enumerate(selected_exercises):
        # AI adjusts sets/reps based on user's fitness level
        custom_sets, custom_reps = ai_calculate_parameters(
            exercise, user.fitness_level, user.progress_history
        )
        
        UserExercise.objects.create(
            user_workout=workout,
            exercise=exercise,
            sets=custom_sets,
            reps=custom_reps,
            rest_time=ai_calculate_rest_time(user.fitness_level),
            order=idx + 1,
            notes=f"AI: {ai_generate_tip(exercise, user)}"
        )
    
    # Step 4: Calculate estimates
    workout.calculate_estimates()
    
    return workout
```

### 2. AI Updates Existing Workout

```python
def ai_adjust_workout_difficulty(user_workout, direction='increase'):
    """
    AI modifies an existing workout based on user feedback.
    """
    for user_exercise in user_workout.user_exercises.all():
        if direction == 'increase':
            user_exercise.sets += 1
            user_exercise.reps = int(user_exercise.reps * 1.1)
        else:
            user_exercise.sets = max(1, user_exercise.sets - 1)
            user_exercise.reps = max(5, int(user_exercise.reps * 0.9))
        
        user_exercise.save()
    
    # Recalculate estimates
    user_workout.calculate_estimates()
```

### 3. AI Recommends Exercises

```python
def ai_recommend_exercises(user, count=5):
    """
    AI recommends exercises based on user's history and goals.
    """
    # Analyze user's workout history
    completed_workouts = user.workouts.filter(
        progress_records__isnull=False
    )
    
    # Find exercises user hasn't done recently
    recent_exercise_ids = UserExercise.objects.filter(
        user_workout__in=completed_workouts
    ).values_list('exercise_id', flat=True).distinct()
    
    # Recommend new exercises matching user's level
    recommended = Exercise.objects.exclude(
        id__in=recent_exercise_ids
    ).filter(
        difficulty=user.fitness_level,
        muscle_group__in=user.target_muscle_groups
    )[:count]
    
    return recommended
```

---

## 📝 Usage Examples

### Example 1: Populate Exercise Library (One-time Setup)

```python
from workouts.models import ExerciseCategory, Exercise

# Create categories
strength = ExerciseCategory.objects.create(
    name="Strength Training",
    description="Resistance exercises"
)

cardio = ExerciseCategory.objects.create(
    name="Cardio",
    description="Cardiovascular exercises"
)

# Add exercises
Exercise.objects.create(
    name="Push-ups",
    description="Classic upper body push exercise",
    video_url="https://example.com/pushups.mp4",
    muscle_group="Chest, Triceps",
    category=strength,
    difficulty="beginner",
    default_sets=3,
    default_reps=10,
    default_rest_time=60,
    calories_per_rep=0.5,
    equipment_needed="None",
    tips="Keep your core engaged and back straight"
)

Exercise.objects.create(
    name="Burpees",
    description="Full body explosive movement",
    video_url="https://example.com/burpees.mp4",
    muscle_group="Full Body",
    category=cardio,
    difficulty="intermediate",
    default_sets=3,
    default_reps=15,
    default_rest_time=90,
    calories_per_rep=1.2,
    equipment_needed="None",
    tips="Land softly and maintain rhythm"
)
```

### Example 2: AI Creates Workout via API

```bash
curl -X POST http://localhost:8000/api/workouts/user-workouts/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Beginner Full Body",
    "description": "Complete workout for beginners",
    "created_by_ai": true,
    "difficulty": "beginner",
    "exercises": [
      {"exercise_id": 1, "sets": 3, "reps": 10, "rest_time": 60, "order": 1},
      {"exercise_id": 2, "sets": 3, "reps": 12, "rest_time": 60, "order": 2},
      {"exercise_id": 3, "sets": 3, "reps": 15, "rest_time": 45, "order": 3}
    ]
  }'
```

### Example 3: User Completes Workout

```bash
curl -X POST http://localhost:8000/api/workouts/progress/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_workout": 1,
    "completed_exercises": [1, 2, 3],
    "actual_duration": 30,
    "actual_calories": 250,
    "rating": 5,
    "difficulty_rating": "just_right"
  }'
```

---

## 🎯 Key Advantages of This Design

1. **Scalable Exercise Library**: Add exercises once, reuse across all users
2. **Personalization**: Each user gets workouts tailored to their level
3. **AI Flexibility**: AI can freely combine and customize exercises
4. **Data Efficiency**: No redundant workout templates
5. **Progress Tracking**: Better insights into what works for each user
6. **Easy Updates**: Update an exercise once, affects all future workouts

---

## 🔄 Migration Strategy

Due to the significant structural changes, consider:

**Option 1: Fresh Start (Recommended for Development)**
```bash
# Backup current database
python manage.py dumpdata > backup.json

# Reset migrations
rm db.sqlite3
rm workouts/migrations/000*.py
python manage.py makemigrations
python manage.py migrate

# Repopulate exercise library
python manage.py populate_exercises
```

**Option 2: Production Migration**
Create custom migration scripts to:
1. Extract exercises from old workouts
2. Deduplicate and create Exercise records
3. Transform UserWorkout assignments
4. Preserve user progress data

---

## 📚 Summary

**Old Design** (Incorrect):
- Pre-built Workout templates in database
- Users select from templates
- AI only customizes parameters

**New Design** (Correct):
- Pre-built Exercise library
- AI creates custom UserWorkouts
- Each workout is unique to the user

This aligns with your original intention of having AI **dynamically create workouts** rather than just assign templates.
