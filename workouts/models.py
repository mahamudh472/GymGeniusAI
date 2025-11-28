from django.db import models
from accounts.models import User
from random import randint


def generate_exercise_name():
    """Generate a unique default name for exercises"""
    return f"Unnamed Exercise_{randint(100000, 999999)}"


def generate_workout_name():
    """Generate a unique default name for workouts"""
    return f"Unnamed Workout_{randint(100000, 999999)}"


class ExerciseCategory(models.Model):
    """Categories for exercises (e.g., Cardio, Strength, Flexibility)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'exercise_categories'
        verbose_name = 'Exercise Category'
        verbose_name_plural = 'Exercise Categories'
    
    def __str__(self):
        return self.name


class Exercise(models.Model):
    """Pre-built exercises that can be used in user workouts"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=150, unique=True, default=generate_exercise_name)
    description = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to='exercise_videos/', blank=True, null=True)
    
    # Exercise classification
    muscle_group = models.CharField(max_length=100, blank=True, null=True, 
                                    help_text="e.g., Chest, Back, Legs, Arms, Core, Full Body")
    category = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, 
                                 related_name='exercises', null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Default parameters (AI can customize these per user)
    default_sets = models.IntegerField(default=3, help_text="Default number of sets")
    default_reps = models.IntegerField(default=10, help_text="Default number of repetitions")
    default_duration_seconds = models.IntegerField(blank=True, null=True, 
                                                   help_text="Default duration in seconds (for timed exercises)")
    default_rest_time = models.IntegerField(default=60, help_text="Default rest time in seconds")
    
    # Metadata
    calories_per_rep = models.FloatField(default=0.5, help_text="Estimated calories burned per rep")
    equipment_needed = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="e.g., Dumbbells, Barbell, None")
    tips = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercises'
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserWorkout(models.Model):
    """User-specific workout dynamically created by AI or manually"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=255, default=generate_workout_name)
    description = models.TextField(blank=True, null=True)
    
    # Workout metadata
    created_by_ai = models.BooleanField(default=False, help_text="Whether this was created by AI")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, blank=True, null=True)
    estimated_duration = models.IntegerField(blank=True, null=True, 
                                            help_text="Estimated duration in minutes")
    estimated_calories = models.IntegerField(blank=True, null=True, 
                                            help_text="Estimated calories to burn")
    
    image = models.ImageField(upload_to='workout_images/', blank=True, null=True)


    # Status and timestamps
    is_active = models.BooleanField(default=True, help_text="Whether this workout is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_workouts'
        verbose_name = 'User Workout'
        verbose_name_plural = 'User Workouts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    def calculate_estimates(self):
        """Calculate estimated duration and calories based on exercises"""
        user_exercises = self.user_exercises.all()
        total_duration = 0
        total_calories = 0
        
        for user_ex in user_exercises:
            # Duration = (sets * (reps * time_per_rep + rest_time))
            # Assuming ~3 seconds per rep
            exercise_time = user_ex.sets * (user_ex.reps * 3 + user_ex.rest_time)
            total_duration += exercise_time
            
            # Calories = sets * reps * calories_per_rep
            total_calories += user_ex.sets * user_ex.reps * user_ex.exercise.calories_per_rep
        
        self.estimated_duration = total_duration // 60  # Convert to minutes
        self.estimated_calories = int(total_calories)
        self.save()


class UserExercise(models.Model):
    """Exercises within a user's workout with customized parameters"""
    user_workout = models.ForeignKey(UserWorkout, on_delete=models.CASCADE, related_name='user_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='user_exercises')
    
    # Customized parameters (can differ from exercise defaults)
    sets = models.IntegerField(default=3, help_text="Number of sets")
    reps = models.IntegerField(default=10, help_text="Number of repetitions per set")
    duration_seconds = models.IntegerField(blank=True, null=True, 
                                          help_text="Duration in seconds (for timed exercises)")
    rest_time = models.IntegerField(default=60, help_text="Rest time in seconds between sets")
    
    # Exercise order and notes
    order = models.IntegerField(default=0, help_text="Order of exercise in workout")
    notes = models.TextField(blank=True, null=True, 
                            help_text="AI-generated or custom notes for this exercise")
    
    class Meta:
        db_table = 'user_exercises'
        verbose_name = 'User Exercise'
        verbose_name_plural = 'User Exercises'
        ordering = ['order']
        unique_together = ['user_workout', 'exercise', 'order']
    
    def __str__(self):
        return f"{self.user_workout.name} - {self.exercise.name}"
    
    def save(self, *args, **kwargs):
        # If not customized, use exercise defaults
        if self.sets is None:
            self.sets = self.exercise.default_sets
        if self.reps is None:
            self.reps = self.exercise.default_reps
        if self.duration_seconds is None:
            self.duration_seconds = self.exercise.default_duration_seconds
        if self.rest_time is None:
            self.rest_time = self.exercise.default_rest_time
        super().save(*args, **kwargs)


class WorkoutProgress(models.Model):
    """Track user workout completion and progress"""
    user_workout = models.ForeignKey(UserWorkout, on_delete=models.CASCADE, related_name='progress_records')
    completed_at = models.DateTimeField(auto_now_add=True)
    
    # Completion tracking
    completed_exercises = models.JSONField(default=list, 
                                          help_text="List of completed user_exercise IDs")
    completion_percentage = models.FloatField(default=0.0, 
                                             help_text="Percentage of exercises completed")
    
    # Actual metrics
    actual_duration = models.IntegerField(blank=True, null=True, 
                                         help_text="Actual duration in minutes")
    actual_calories = models.FloatField(blank=True, null=True, 
                                       help_text="Actual calories burned")
    
    # User feedback
    notes = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True, 
                                help_text="User rating (1-5)")
    difficulty_rating = models.CharField(max_length=20, blank=True, null=True,
                                        choices=[
                                            ('too_easy', 'Too Easy'),
                                            ('just_right', 'Just Right'),
                                            ('too_hard', 'Too Hard'),
                                        ])
    
    class Meta:
        db_table = 'workout_progress'
        verbose_name = 'Workout Progress'
        verbose_name_plural = 'Workout Progress Records'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user_workout.user.email} - {self.user_workout.name} - {self.completed_at.date()}"
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage based on completed exercises"""
        total_exercises = self.user_workout.user_exercises.count()
        if total_exercises == 0:
            return 0.0
        completed_count = len(self.completed_exercises)
        return (completed_count / total_exercises) * 100


class Activity(models.Model):
    """Track user activities with name, duration, and calories burned"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255, help_text="Name of the activity")
    duration = models.IntegerField(help_text="Duration in minutes")
    calories = models.FloatField(help_text="Calories burned during the activity")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.created_at.date()})"


class CustomRoutine(models.Model):
    """One custom routine per user where they can add their favorite exercises"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_routine')
    name = models.CharField(max_length=255, default="My Custom Routine")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'custom_routines'
        verbose_name = 'Custom Routine'
        verbose_name_plural = 'Custom Routines'
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class CustomRoutineExercise(models.Model):
    """Exercises added to a user's custom routine"""
    custom_routine = models.ForeignKey(CustomRoutine, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='custom_routines')
    
    # Customized parameters (user can customize these)
    sets = models.IntegerField(null=True, blank=True, help_text="Number of sets")
    reps = models.IntegerField(null=True, blank=True, help_text="Number of repetitions per set")
    duration_seconds = models.IntegerField(blank=True, null=True, 
                                          help_text="Duration in seconds (for timed exercises)")
    rest_time = models.IntegerField(null=True, blank=True, help_text="Rest time in seconds between sets")
    
    # Exercise order and notes
    order = models.IntegerField(default=0, help_text="Order of exercise in routine")
    notes = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'custom_routine_exercises'
        verbose_name = 'Custom Routine Exercise'
        verbose_name_plural = 'Custom Routine Exercises'
        ordering = ['order', 'added_at']
        unique_together = ['custom_routine', 'exercise']
    
    def __str__(self):
        return f"{self.custom_routine.user.email} - {self.exercise.name}"
    
    def save(self, *args, **kwargs):
        # If not customized, use exercise defaults
        if self.sets is None:
            self.sets = self.exercise.default_sets
        if self.reps is None:
            self.reps = self.exercise.default_reps
        if self.duration_seconds is None:
            self.duration_seconds = self.exercise.default_duration_seconds
        if self.rest_time is None:
            self.rest_time = self.exercise.default_rest_time
        super().save(*args, **kwargs)
    
    def calculate_calories(self):
        """Calculate estimated calories for this exercise"""
        if self.sets and self.reps:
            return self.sets * self.reps * self.exercise.calories_per_rep
        return 0.0
    
    def calculate_duration(self):
        """Calculate estimated duration in minutes for this exercise"""
        if self.duration_seconds:
            # For timed exercises
            total_seconds = self.sets * self.duration_seconds
            if self.rest_time:
                total_seconds += (self.sets - 1) * self.rest_time
        elif self.sets and self.reps:
            # For rep-based exercises, assume ~3 seconds per rep
            total_seconds = self.sets * (self.reps * 3)
            if self.rest_time:
                total_seconds += (self.sets - 1) * self.rest_time
        else:
            return 0
        
        return total_seconds // 60  # Convert to minutes


class CustomRoutineExerciseCompletion(models.Model):
    """Track completion of individual exercises in custom routine"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_exercise_completions')
    custom_routine_exercise = models.ForeignKey(CustomRoutineExercise, on_delete=models.CASCADE, 
                                                 related_name='completions')
    
    # Actual performance
    actual_sets = models.IntegerField(help_text="Actual sets completed")
    actual_reps = models.IntegerField(blank=True, null=True, help_text="Actual reps completed per set")
    actual_duration_seconds = models.IntegerField(blank=True, null=True, 
                                                  help_text="Actual duration in seconds")
    
    # Metrics
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    calories_burned = models.FloatField(help_text="Estimated calories burned")
    
    # Feedback
    notes = models.TextField(blank=True, null=True)
    difficulty_rating = models.CharField(max_length=20, blank=True, null=True,
                                        choices=[
                                            ('easy', 'Easy'),
                                            ('moderate', 'Moderate'),
                                            ('hard', 'Hard'),
                                        ])
    
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'custom_routine_exercise_completions'
        verbose_name = 'Custom Routine Exercise Completion'
        verbose_name_plural = 'Custom Routine Exercise Completions'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.custom_routine_exercise.exercise.name} - {self.completed_at.date()}"
