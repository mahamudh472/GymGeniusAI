from rest_framework import serializers
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity
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
    video_url = serializers.CharField(source='exercise.video_url', read_only=True)
    difficulty_level = serializers.CharField(source='exercise.difficulty_level', read_only=True)
    class Meta:
        model = UserExercise
        fields = '__all__'

class UserWorkoutListSerializer(serializers.ModelSerializer):
    exercise_count = serializers.IntegerField(source='user_exercises.count', read_only=True)
    class Meta:
        model = UserWorkout
        fields = ['id', 'name', 'description', 'estimated_duration', 'estimated_calories', 'exercise_count', 'difficulty']
        
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
        fields = ['id', 'name', 'description', 'estimated_duration', 'estimated_calories', 'user_exercises', 'exercise_count']

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