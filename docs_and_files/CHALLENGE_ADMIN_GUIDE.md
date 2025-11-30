# Challenge Admin Interface - User Guide

## Overview

The Challenge Admin Interface provides a user-friendly way to create and manage workout challenges with dynamic exercise selection. This custom Django admin interface uses django-unfold for a modern, intuitive experience.

## Features

### 1. **Dynamic Exercise Selection**
- Choose exercises from the Exercise database
- Automatically enriches with exercise details (video, description, tips, etc.)
- Modify sets, reps, duration, and rest time for each exercise

### 2. **Automatic Calculations**
- **Estimated Duration**: Automatically calculated based on sets, reps, and rest times
- **Estimated Calories**: Calculated using exercise calories_per_rep and workout structure

### 3. **Flexible Exercise Management**
- Add unlimited exercises to a challenge
- Remove exercises dynamically
- Reorder exercises visually
- Each exercise shows its number in the sequence

### 4. **Smart Form Validation**
- Ensures at least one exercise is added
- Validates that dates are properly set
- Checks all required fields before submission

## How to Use

### Creating a New Challenge

1. **Access the Admin Interface**
   - Navigate to: `http://localhost:8000/admin/gamification/challenge/`
   - Click "Add Challenge" button

2. **Fill Basic Information**
   - **Name**: Give your challenge a catchy name (e.g., "Morning Power Challenge")
   - **Description**: Describe what the challenge is about
   - **Challenge Type**: Choose DAILY or WEEKLY
   - **Difficulty**: Select beginner, intermediate, or advanced
   - **Completion Points**: Set reward points (e.g., 100 for daily, 500 for weekly)

3. **Set Duration**
   - **Start Date**: When users can start the challenge
   - **End Date**: When the challenge expires
   - Use datetime picker for easy selection

4. **Add Exercises**
   
   For each exercise:
   - **Exercise**: Select from dropdown (searchable)
   - **Sets**: Number of sets (default: 3)
   - **Reps**: Repetitions per set (optional for timed exercises)
   - **Duration (s)**: For timed exercises like planks (optional)
   - **Rest (s)**: Rest time between sets in seconds (default: 60)
   - **Notes**: Add specific instructions (optional)
   
   **Example 1: Rep-based Exercise**
   ```
   Exercise: Push-ups
   Sets: 3
   Reps: 15
   Rest: 60s
   Notes: Keep your back straight and core engaged
   ```
   
   **Example 2: Timed Exercise**
   ```
   Exercise: Plank
   Sets: 3
   Duration: 60s
   Rest: 45s
   Notes: Don't let your hips sag
   ```

5. **Add More Exercises**
   - Click "+ Add Another Exercise" button
   - Repeat for each exercise you want to include
   - Remove unwanted exercises with "Remove" button

6. **Set Status**
   - Check "Is Active" to make challenge visible to users
   - Uncheck to keep it as draft

7. **Save**
   - Click "Create Challenge" to save
   - System automatically calculates duration and calories
   - Redirects to challenge list with success message

### Editing an Existing Challenge

1. **Access Challenge List**
   - Go to: `http://localhost:8000/admin/gamification/challenge/`
   - Find the challenge you want to edit

2. **Click Challenge Name**
   - Opens the custom edit form
   - Pre-populated with existing data
   - Exercises are loaded automatically

3. **Make Changes**
   - Modify any field
   - Add/remove exercises
   - Update exercise parameters

4. **Save Changes**
   - Click "Update Challenge"
   - Calculations are updated automatically

## Field Descriptions

### Basic Fields

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| Name | Challenge title | Yes | "7-Day Strength Builder" |
| Description | Detailed description | Yes | "Build strength with this progressive challenge" |
| Challenge Type | DAILY or WEEKLY | Yes | WEEKLY |
| Difficulty | beginner, intermediate, advanced | Yes | intermediate |
| Completion Points | Reward points | Yes | 500 |
| Start Date | When challenge starts | Yes | 2025-12-01 00:00 |
| End Date | When challenge ends | Yes | 2025-12-07 23:59 |
| Is Active | Visibility status | No | ✓ (checked) |

### Exercise Fields

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| Exercise | Exercise from database | Yes | "Push-ups" |
| Sets | Number of sets | Yes | 3 |
| Reps | Reps per set | No* | 15 |
| Duration (s) | Time in seconds | No* | 60 |
| Rest (s) | Rest between sets | Yes | 60 |
| Notes | Custom instructions | No | "Focus on form" |

*Either Reps or Duration should be provided (or both for mixed exercises)

## Tips & Best Practices

### 1. **Challenge Duration**
- **Daily Challenges**: 24 hours (one day)
- **Weekly Challenges**: 7 days (one week)
- Ensure end_date > start_date

### 2. **Exercise Selection**
- Mix different muscle groups for balanced workouts
- Start with easier exercises for warmup
- End with core or stretching exercises
- Consider the target difficulty level

### 3. **Sets and Reps**
- **Beginner**: 2-3 sets, 8-12 reps
- **Intermediate**: 3-4 sets, 12-15 reps
- **Advanced**: 4-5 sets, 15-20 reps

### 4. **Rest Times**
- **Strength exercises**: 60-90 seconds
- **Cardio exercises**: 30-45 seconds
- **High-intensity**: 45-60 seconds
- **Core/Plank**: 30-45 seconds

### 5. **Completion Points**
Base points on:
- Number of exercises (more = more points)
- Difficulty level (advanced = more points)
- Time commitment (weekly = more points)

**Suggested Points:**
- Daily Beginner: 50-100 points
- Daily Intermediate: 100-150 points
- Daily Advanced: 150-200 points
- Weekly Beginner: 300-400 points
- Weekly Intermediate: 400-600 points
- Weekly Advanced: 600-1000 points

## Example Challenges

### Example 1: Quick Morning Challenge (DAILY, Beginner)

```
Name: "Morning Energizer"
Description: "Start your day with a quick 15-minute workout"
Type: DAILY
Difficulty: beginner
Points: 75
Duration: Today 6:00 AM - Today 11:59 PM

Exercises:
1. Jumping Jacks - 3 sets, 20 reps, 30s rest
2. Push-ups - 3 sets, 10 reps, 60s rest
3. Bodyweight Squats - 3 sets, 15 reps, 45s rest
4. Plank - 3 sets, 30s duration, 30s rest

Result: ~15 min, ~120 calories
```

### Example 2: Full Body Weekly Challenge (WEEKLY, Intermediate)

```
Name: "Full Body Transformation"
Description: "Complete this challenging weekly workout to earn big points"
Type: WEEKLY
Difficulty: intermediate
Points: 500
Duration: Monday 00:00 - Sunday 23:59

Exercises:
1. Push-ups - 4 sets, 15 reps, 60s rest
2. Pull-ups - 4 sets, 8 reps, 90s rest
3. Squats - 4 sets, 20 reps, 60s rest
4. Lunges - 4 sets, 12 reps, 60s rest
5. Plank - 4 sets, 60s duration, 45s rest
6. Mountain Climbers - 3 sets, 30 reps, 45s rest
7. Burpees - 3 sets, 15 reps, 90s rest

Result: ~45 min, ~400 calories
```

## Troubleshooting

### Issue: "A challenge must have at least one exercise"
**Solution**: Add at least one exercise before saving

### Issue: Estimated values not showing
**Solution**: They calculate after saving. Check the challenge list or detail view

### Issue: Exercise dropdown empty
**Solution**: Ensure exercises exist in the Exercise model (workouts app)

### Issue: Can't save challenge
**Solution**: Check all required fields are filled and all errors are resolved

## Technical Details

### File Structure
```
gamification/
├── admin.py                 # Custom admin with views
├── forms.py                 # Challenge and exercise forms
├── templates/
│   └── admin/
│       └── gamification/
│           ├── challenge_form.html      # Create/Edit form
│           └── challenge_changelist.html # List view
└── models.py               # Challenge model
```

### How It Works

1. **Form Submission**: User fills form and adds exercises
2. **Formset Processing**: Each exercise form is validated
3. **JSON Building**: Exercise data converted to JSON format with exercise_id
4. **Calculation**: Duration and calories automatically calculated
5. **Database Save**: Challenge saved with exercises JSON
6. **API Response**: When fetched via API, exercises are enriched with full details

### Calculations

**Duration Formula:**
```python
# For rep-based exercises
duration = sets * (reps * 3_seconds + rest_time)

# For timed exercises
duration = sets * (duration_seconds + rest_time)

# Total
estimated_duration = sum(all_exercises) / 60  # in minutes
```

**Calories Formula:**
```python
# For rep-based exercises
calories = sets * reps * exercise.calories_per_rep

# For timed exercises
calories = sets * duration_seconds * 0.1  # rough estimate

# Total
estimated_calories = sum(all_exercises)
```

## Support

For technical issues or questions about the challenge admin interface:
- Check the gamification app documentation
- Review the Challenge model in `gamification/models.py`
- See API documentation in `docs_and_files/CHALLENGE_API_DOCUMENTATION.md`
