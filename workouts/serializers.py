from rest_framework import serializers
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity,
    CustomRoutine, CustomRoutineExercise, CustomRoutineExerciseCompletion
)


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseCategory
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class UserExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    exercise_description = serializers.CharField(source='exercise.description', read_only=True)
    # video_url = serializers.CharField(source='exercise.video_url', read_only=True)
    difficulty_level = serializers.CharField(source='exercise.difficulty_level', read_only=True)
    video=serializers.SerializerMethodField()

    def get_video(self, obj):
        request = self.context.get('request')
        video = obj.exercise.videos.filter(exercise=obj.exercise, coach__name=request.user.coach_type.name).first()
        print("EXERCISE:", obj.exercise.name)
        print("user_exercise:", obj.id)
        print("Coach Type:", request.user.coach_type)
        print("VIDEO URL:", video)
        if not video:
            return None
        if video.video_file and hasattr(video.video_file, 'url'):
            return request.build_absolute_uri(video.video_file.url)
        return None

    class Meta:
        model = UserExercise
        fields = '__all__'

class UserWorkoutListSerializer(serializers.ModelSerializer):
    exercise_count = serializers.IntegerField(source='user_exercises.count', read_only=True)
    class Meta:
        model = UserWorkout
        fields = ['id', 'name', 'description', 'image', 'estimated_duration', 'estimated_calories', 'exercise_count', 'difficulty']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['estimated_duration'] = f"{instance.estimated_duration} minutes"
        representation['estimated_calories'] = f"{instance.estimated_calories} kcal"
        return representation

class UserWorkoutSerializer(serializers.ModelSerializer):
    user_exercises = UserExerciseSerializer(many=True)
    exercise_count = serializers.IntegerField(source='user_exercises.count', read_only=True)
    class Meta:
        model = UserWorkout
        fields = ['id', 'name', 'description', 'image', 'estimated_duration', 'estimated_calories', 'user_exercises', 'exercise_count']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['estimated_duration'] = f"{instance.estimated_duration} minutes"
        representation['estimated_calories'] = f"{instance.estimated_calories} kcal"
        return representation



class WorkoutProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgress
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class CompleteExerciseSerializer(serializers.Serializer):
    """Serializer for marking an exercise as completed in a workout"""
    user_workout_id = serializers.IntegerField(required=True)
    user_exercise_id = serializers.IntegerField(required=True)
    actual_sets = serializers.IntegerField(required=False, allow_null=True)
    actual_reps = serializers.IntegerField(required=False, allow_null=True)
    actual_duration = serializers.IntegerField(required=False, allow_null=True, help_text="Actual duration in seconds")
    notes = serializers.CharField(required=False, allow_blank=True)


class CustomRoutineExerciseSerializer(serializers.ModelSerializer):
    """Serializer for exercises in custom routine with full exercise details"""
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    exercise_description = serializers.CharField(source='exercise.description', read_only=True)
    video_url = serializers.URLField(source='exercise.video_url', read_only=True)
    muscle_group = serializers.CharField(source='exercise.muscle_group', read_only=True)
    difficulty = serializers.CharField(source='exercise.difficulty', read_only=True)
    equipment_needed = serializers.CharField(source='exercise.equipment_needed', read_only=True)
    
    class Meta:
        model = CustomRoutineExercise
        fields = [
            'id', 'exercise', 'exercise_name', 'exercise_description', 'video_url',
            'muscle_group', 'difficulty', 'equipment_needed', 'sets', 'reps', 
            'duration_seconds', 'rest_time', 'order', 'notes', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class CustomRoutineSerializer(serializers.ModelSerializer):
    """Serializer for custom routine with all exercises"""
    exercises = CustomRoutineExerciseSerializer(many=True, read_only=True)
    exercise_count = serializers.IntegerField(source='exercises.count', read_only=True)
    
    class Meta:
        model = CustomRoutine
        fields = ['id', 'name', 'description', 'exercise_count', 'exercises', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ToggleExerciseSerializer(serializers.Serializer):
    """Serializer for toggling an exercise in custom routine"""
    exercise_id = serializers.IntegerField(required=True, help_text="ID of the exercise to toggle")


class CompleteCustomRoutineExerciseSerializer(serializers.Serializer):
    """Serializer for completing a custom routine exercise"""
    custom_routine_exercise_id = serializers.IntegerField(required=True, 
                                                          help_text="ID of the custom routine exercise to complete")
    actual_sets = serializers.IntegerField(required=True, help_text="Number of sets completed")
    actual_reps = serializers.IntegerField(required=False, allow_null=True, 
                                          help_text="Number of reps completed per set")
    actual_duration_seconds = serializers.IntegerField(required=False, allow_null=True, 
                                                       help_text="Actual duration in seconds for timed exercises")
    duration_minutes = serializers.IntegerField(required=True, help_text="Total duration in minutes")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Optional notes")
    difficulty_rating = serializers.ChoiceField(
        choices=['easy', 'moderate', 'hard'],
        required=False,
        allow_null=True,
        help_text="How difficult was the exercise"
    )


class CustomRoutineExerciseCompletionSerializer(serializers.ModelSerializer):
    """Serializer for custom routine exercise completion records"""
    exercise_name = serializers.CharField(source='custom_routine_exercise.exercise.name', read_only=True)
    
    class Meta:
        model = CustomRoutineExerciseCompletion
        fields = '__all__'
        read_only_fields = ['user', 'completed_at', 'calories_burned']


class DailyProgressSerializer(serializers.Serializer):
    """Serializer for daily progress summary"""
    date = serializers.DateField(help_text="The date for which progress is calculated")
    progress_percentage = serializers.FloatField(help_text="Workout completion percentage for the day")
    calories_burned = serializers.FloatField(help_text="Total calories burned from completed workouts")
    total_training_time = serializers.IntegerField(help_text="Total training time in minutes")
    activities = ActivitySerializer(many=True, help_text="List of activities completed on this day")
    workout_details = serializers.DictField(required=False, help_text="Details about the workout for the day")