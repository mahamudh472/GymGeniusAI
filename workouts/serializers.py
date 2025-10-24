from rest_framework import serializers
from .models import WorkoutCategory, Workout, WorkoutRound, Exercise, UserWorkoutProgress

class WorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = ['id', 'name', 'description']

class WorkoutSerializer(serializers.ModelSerializer):
    category = WorkoutCategorySerializer()
    
    class Meta:
        model = Workout
        fields = ['id', 'title', 'description', 'video_url', 'difficulty', 'category', 'calories_burn', 'duration_minutes']

class WorkoutRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutRound
        fields = ['id', 'workout', 'name', 'round_order']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'round', 'name', 'reps', 'sets', 'rest_seconds', 'video_url', 'tips']
        
class UserWorkoutProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWorkoutProgress
        fields = ['id', 'user', 'workout', 'date', 'calories_burned', 'duration_minutes']
