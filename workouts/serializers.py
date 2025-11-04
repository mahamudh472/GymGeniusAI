from rest_framework import serializers
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress
)


class ExerciseCategorySerializer(serializers.ModelSerializer):
    """Serializer for exercise categories"""
    class Meta:
        model = ExerciseCategory
        fields = ['id', 'name', 'description']


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for pre-built exercises"""
    category = ExerciseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ExerciseCategory.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'description', 'video_url', 'muscle_group',
            'category', 'category_id', 'difficulty', 'default_sets',
            'default_reps', 'default_duration_seconds', 'default_rest_time',
            'calories_per_rep', 'equipment_needed', 'tips',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExerciseListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing exercises"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'muscle_group', 'category_name', 'difficulty',
            'default_sets', 'default_reps', 'default_rest_time', 'equipment_needed'
        ]


class UserExerciseSerializer(serializers.ModelSerializer):
    """Serializer for exercises within a user's workout"""
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    exercise_video_url = serializers.URLField(source='exercise.video_url', read_only=True)
    
    class Meta:
        model = UserExercise
        fields = [
            'id', 'exercise', 'exercise_id', 'exercise_name', 'exercise_video_url',
            'sets', 'reps', 'duration_seconds', 'rest_time', 'order', 'notes'
        ]
    
    def validate(self, data):
        """Use exercise defaults if values not provided"""
        if 'exercise' in data:
            exercise = data['exercise']
            if 'sets' not in data or data.get('sets') is None:
                data['sets'] = exercise.default_sets
            if 'reps' not in data or data.get('reps') is None:
                data['reps'] = exercise.default_reps
            if 'rest_time' not in data or data.get('rest_time') is None:
                data['rest_time'] = exercise.default_rest_time
            if 'duration_seconds' not in data or data.get('duration_seconds') is None:
                data['duration_seconds'] = exercise.default_duration_seconds
        return data


class UserExerciseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user exercises (used with workout creation)"""
    class Meta:
        model = UserExercise
        fields = ['exercise_id', 'sets', 'reps', 'duration_seconds', 'rest_time', 'order', 'notes']
    
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise'
    )


class UserWorkoutSerializer(serializers.ModelSerializer):
    """Full serializer for user workouts"""
    user_exercises = UserExerciseSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    total_exercises = serializers.SerializerMethodField()
    
    class Meta:
        model = UserWorkout
        fields = [
            'id', 'user', 'user_email', 'user_name', 'name', 'description',
            'created_by_ai', 'difficulty', 'estimated_duration',
            'estimated_calories', 'is_active', 'user_exercises',
            'total_exercises', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'estimated_duration', 'estimated_calories']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def get_total_exercises(self, obj):
        return obj.user_exercises.count()


class UserWorkoutListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing user workouts"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    total_exercises = serializers.SerializerMethodField()
    
    class Meta:
        model = UserWorkout
        fields = [
            'id', 'user_email', 'name', 'difficulty', 'created_by_ai',
            'estimated_duration', 'estimated_calories', 'is_active',
            'total_exercises', 'created_at'
        ]
    
    def get_total_exercises(self, obj):
        return obj.user_exercises.count()


class UserWorkoutCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workouts with nested exercises"""
    exercises = UserExerciseCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = UserWorkout
        fields = [
            'name', 'description', 'created_by_ai', 'difficulty',
            'is_active', 'exercises'
        ]
    
    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises', [])
        user = self.context['request'].user
        user_workout = UserWorkout.objects.create(user=user, **validated_data)
        
        for exercise_data in exercises_data:
            UserExercise.objects.create(user_workout=user_workout, **exercise_data)
        
        # Calculate estimates based on exercises
        user_workout.calculate_estimates()
        
        return user_workout


class WorkoutProgressSerializer(serializers.ModelSerializer):
    """Serializer for tracking workout completion"""
    user_workout = UserWorkoutListSerializer(read_only=True)
    user_workout_id = serializers.PrimaryKeyRelatedField(
        queryset=UserWorkout.objects.all(),
        source='user_workout',
        write_only=True
    )
    workout_name = serializers.CharField(source='user_workout.name', read_only=True)
    user_email = serializers.EmailField(source='user_workout.user.email', read_only=True)
    
    class Meta:
        model = WorkoutProgress
        fields = [
            'id', 'user_workout', 'user_workout_id', 'workout_name', 'user_email',
            'completed_at', 'completed_exercises', 'completion_percentage',
            'actual_duration', 'actual_calories', 'notes', 'rating', 'difficulty_rating'
        ]
        read_only_fields = ['completed_at']
    
    def create(self, validated_data):
        progress = super().create(validated_data)
        # Calculate completion percentage
        progress.completion_percentage = progress.calculate_completion_percentage()
        progress.save()
        return progress


class WorkoutProgressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workout progress records"""
    class Meta:
        model = WorkoutProgress
        fields = [
            'user_workout', 'completed_exercises', 'actual_duration',
            'actual_calories', 'notes', 'rating', 'difficulty_rating'
        ]
