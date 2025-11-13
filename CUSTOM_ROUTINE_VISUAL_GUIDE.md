# Custom Routine Feature - Visual Guide

## Database Schema

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│      User       │         │   CustomRoutine      │         │    Exercise     │
├─────────────────┤         ├──────────────────────┤         ├─────────────────┤
│ id (PK)         │◄───1:1──│ id (PK)              │         │ id (PK)         │
│ email           │         │ user_id (FK, Unique) │         │ name            │
│ first_name      │         │ name                 │         │ description     │
│ ...             │         │ description          │         │ muscle_group    │
└─────────────────┘         │ created_at           │         │ difficulty      │
                            │ updated_at           │         │ default_sets    │
                            └──────────────────────┘         │ default_reps    │
                                       │                     │ ...             │
                                       │                     └─────────────────┘
                                       │                              │
                                       │1                             │
                                       │                              │
                                       │                              │
                                       │N                            │N
                                       │                              │
                            ┌──────────▼──────────────────────────────▼────┐
                            │      CustomRoutineExercise (Junction)        │
                            ├──────────────────────────────────────────────┤
                            │ id (PK)                                      │
                            │ custom_routine_id (FK)                       │
                            │ exercise_id (FK)                             │
                            │ sets (nullable)                              │
                            │ reps (nullable)                              │
                            │ duration_seconds (nullable)                  │
                            │ rest_time (nullable)                         │
                            │ order                                        │
                            │ notes                                        │
                            │ added_at                                     │
                            │ UNIQUE(custom_routine_id, exercise_id)       │
                            └──────────────────────────────────────────────┘
```

## API Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CUSTOM ROUTINE WORKFLOW                          │
└──────────────────────────────────────────────────────────────────────────┘

1. USER VIEWS EXERCISE LIBRARY
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ GET /api/workouts/exercises/
          │ ?muscle_group=Chest&difficulty=beginner
          ▼
   ┌──────────────┐
   │   Backend    │ ──► Returns: List of exercises with details
   └──────────────┘


2. FRONTEND CHECKS WHICH EXERCISES ARE IN ROUTINE
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ GET /api/workouts/custom-routine/
          ▼
   ┌──────────────┐
   │   Backend    │ ──► Returns: Custom routine with exercises
   └──────────────┘
          │
          ▼
   [Exercise IDs: 1, 5, 12] ──► Used to highlight "added" state


3. USER CLICKS "ADD" BUTTON (Exercise not in routine)
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ POST /api/workouts/custom-routine/toggle-exercise/
          │ { "exercise_id": 3 }
          ▼
   ┌──────────────┐
   │   Backend    │ ──► Checks if exercise exists in routine
   └──────┬───────┘
          │ Not found ──► Creates CustomRoutineExercise
          ▼
   Response: {
     "action": "added",
     "message": "Exercise added to custom routine",
     "exercise": { ... },
     "custom_routine": { ... }
   }
          │
          ▼
   ┌──────────────┐
   │   Frontend   │ ──► Updates UI: Button changes to "Remove"
   └──────────────┘


4. USER CLICKS "REMOVE" BUTTON (Exercise in routine)
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ POST /api/workouts/custom-routine/toggle-exercise/
          │ { "exercise_id": 3 }
          ▼
   ┌──────────────┐
   │   Backend    │ ──► Checks if exercise exists in routine
   └──────┬───────┘
          │ Found ──► Deletes CustomRoutineExercise
          ▼
   Response: {
     "action": "removed",
     "message": "Exercise removed from custom routine",
     "exercise": null,
     "custom_routine": { ... }
   }
          │
          ▼
   ┌──────────────┐
   │   Frontend   │ ──► Updates UI: Button changes to "Add"
   └──────────────┘


5. USER VIEWS THEIR CUSTOM ROUTINE
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ GET /api/workouts/custom-routine/exercises/
          ▼
   ┌──────────────┐
   │   Backend    │ ──► Returns: List of exercises in routine
   └──────────────┘        ordered by 'order' field
          │
          ▼
   [
     { id: 1, exercise_name: "Push-ups", order: 1, ... },
     { id: 2, exercise_name: "Squats", order: 2, ... },
     { id: 3, exercise_name: "Plank", order: 3, ... }
   ]
```

## UI State Management

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXERCISE CARD STATES                          │
└─────────────────────────────────────────────────────────────────────┘

INITIAL LOAD:
┌─────────────────────────────────┐
│ Frontend loads:                 │
│ 1. All exercises               │
│ 2. Custom routine with exercise│
│    IDs                          │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Create Set of added exercise IDs│
│ e.g., Set([1, 5, 12])           │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Render each exercise card:      │
│                                 │
│  If exerciseId in Set:          │
│    ┌──────────────────────┐    │
│    │ [✓ Remove] Button    │    │
│    │ (Red/Secondary)      │    │
│    └──────────────────────┘    │
│                                 │
│  Else:                          │
│    ┌──────────────────────┐    │
│    │ [+ Add] Button       │    │
│    │ (Green/Primary)      │    │
│    └──────────────────────┘    │
└─────────────────────────────────┘


ON BUTTON CLICK:
         │
         ▼
┌─────────────────────────────────┐
│ Call toggle API                 │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ If action === "added":          │
│   - Add exerciseId to Set       │
│   - Change button to "Remove"   │
│   - Show success message        │
│                                 │
│ If action === "removed":        │
│   - Remove exerciseId from Set  │
│   - Change button to "Add"      │
│   - Show success message        │
└─────────────────────────────────┘
```

## React Component Structure Example

```jsx
ExerciseLibraryPage
├── Header
│   └── "Exercise Library" title
│   └── Custom routine count
│
├── FilterBar
│   ├── MuscleGroupFilter (dropdown)
│   ├── DifficultyFilter (dropdown)
│   └── SearchInput
│
└── ExerciseGrid
    ├── ExerciseCard (for each exercise)
    │   ├── ExerciseImage/Video
    │   ├── ExerciseName
    │   ├── ExerciseDescription
    │   ├── ExerciseMetadata
    │   │   ├── Muscle Group badge
    │   │   ├── Difficulty badge
    │   │   └── Equipment needed
    │   └── ToggleButton
    │       ├── "Add to Routine" (if not added)
    │       └── "Remove from Routine" (if added)
    │
    └── [Pagination or Infinite Scroll]


CustomRoutinePage
├── Header
│   ├── Routine name (editable)
│   └── Edit button
│
├── RoutineStats
│   ├── Total exercises
│   ├── Estimated duration
│   └── Estimated calories
│
└── ExerciseList
    ├── CustomRoutineExerciseCard (for each)
    │   ├── Order indicator (#1, #2, etc.)
    │   ├── Exercise details
    │   ├── Sets/Reps display
    │   ├── Remove button
    │   └── Edit button (customize sets/reps)
    │
    └── EmptyState (if no exercises)
        └── "Add exercises from library"
```

## Feature Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                    KEY FEATURES                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ ONE ROUTINE PER USER                                     │
│    └── OneToOneField enforces this at database level        │
│                                                              │
│  ✓ TOGGLE FUNCTIONALITY                                     │
│    └── Single endpoint for add/remove                       │
│    └── Returns action type for UI feedback                  │
│                                                              │
│  ✓ AUTO-CREATION                                            │
│    └── Routine created on first access                      │
│    └── No manual setup required                             │
│                                                              │
│  ✓ DUPLICATE PREVENTION                                     │
│    └── Database constraint prevents duplicates              │
│    └── Toggle removes if already exists                     │
│                                                              │
│  ✓ ORDER MANAGEMENT                                         │
│    └── Exercises ordered by when added                      │
│    └── Maintains consistent ordering                        │
│                                                              │
│  ✓ DEFAULT VALUES                                           │
│    └── Inherits from Exercise model                         │
│    └── Can be customized per user                           │
│                                                              │
│  ✓ FULL EXERCISE INFO                                       │
│    └── All exercise details in responses                    │
│    └── No need for additional API calls                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Example User Journey

```
Step 1: User opens Exercise Library
        ↓
        Sees grid of exercises with "Add to Routine" buttons

Step 2: User clicks "Add" on "Push-ups"
        ↓
        API call → Exercise added to routine
        ↓
        Button changes to "Remove from Routine"
        ↓
        Success message: "Push-ups added to custom routine"

Step 3: User adds "Squats" and "Plank"
        ↓
        Routine now has 3 exercises

Step 4: User navigates to "My Custom Routine"
        ↓
        Sees list of 3 exercises:
        1. Push-ups (3 sets × 10 reps)
        2. Squats (4 sets × 12 reps)
        3. Plank (3 sets × 30 seconds)

Step 5: User changes mind about Push-ups
        ↓
        Clicks "Remove from Routine"
        ↓
        API call → Exercise removed
        ↓
        Routine now has 2 exercises

Step 6: User can start workout from routine
        ↓
        (Future enhancement: Convert to UserWorkout)
```

## Security & Permissions

```
All endpoints require:
┌─────────────────────────────────┐
│ 1. Valid JWT Token              │
│ 2. Active User Status           │
│ 3. User can only access their   │
│    own custom routine           │
└─────────────────────────────────┘

Automatic isolation:
- Filter by request.user
- OneToOne relationship ensures privacy
- No cross-user data access possible
```
