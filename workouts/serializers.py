from rest_framework import serializers
from .models import WorkoutCategory, Workout, WorkoutRound, Exercise, UserWorkoutProgress

class WorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = ['id', 'name', 'description']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'round', 'name', 'reps', 'sets', 'rest_seconds', 'video_url', 'tips']
      

class WorkoutRoundSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True)

    class Meta:
        model = WorkoutRound
        fields = ['id', 'name', 'round_order', 'exercises']



class WorkoutSerializer(serializers.ModelSerializer):
    category = WorkoutCategorySerializer()
    rounds = WorkoutRoundSerializer(many=True)

    class Meta:
        model = Workout
        fields = ['id', 'rounds', 'title', 'description', 'video_url', 'difficulty', 'category', 'calories_burn', 'duration_minutes']

  
class UserWorkoutProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWorkoutProgress
        fields = ['id', 'user', 'workout', 'date', 'calories_burned', 'duration_minutes']
