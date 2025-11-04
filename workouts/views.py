from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseSerializer, ExerciseListSerializer,
    UserWorkoutSerializer, UserWorkoutListSerializer, UserWorkoutCreateSerializer,
    UserExerciseSerializer, WorkoutProgressSerializer, WorkoutProgressCreateSerializer
)
from accounts.permissions import IsActiveUser


class ExerciseCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing exercise categories.
    
    list: Get all exercise categories
    retrieve: Get a specific category
    create: Create a new category (admin only)
    update: Update a category (admin only)
    destroy: Delete a category (admin only)
    """
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    permission_classes = [IsActiveUser]


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pre-built exercises.
    
    list: Get all available exercises (with filtering options)
    retrieve: Get detailed exercise information
    create: Create a new exercise (admin only)
    update: Update an exercise (admin only)
    destroy: Delete an exercise (admin only)
    """
    queryset = Exercise.objects.all().select_related('category')
    permission_classes = [IsActiveUser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseListSerializer
        return ExerciseSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by muscle group
        muscle_group = self.request.query_params.get('muscle_group', None)
        if muscle_group:
            queryset = queryset.filter(muscle_group__icontains=muscle_group)
        
        # Filter by equipment
        equipment = self.request.query_params.get('equipment', None)
        if equipment:
            queryset = queryset.filter(equipment_needed__icontains=equipment)
        
        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class UserWorkoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user workouts.
    
    list: Get all workouts for the current user
    retrieve: Get details of a specific workout
    create: Create a new workout for the user
    update: Update workout details
    destroy: Delete a workout
    partial_update: Update specific fields (e.g., is_active)
    """
    permission_classes = [IsActiveUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserWorkoutCreateSerializer
        elif self.action == 'list':
            return UserWorkoutListSerializer
        return UserWorkoutSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = UserWorkout.objects.filter(user=user).prefetch_related(
            'user_exercises', 'user_exercises__exercise'
        )
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by created_by_ai
        created_by_ai = self.request.query_params.get('created_by_ai', None)
        if created_by_ai is not None:
            queryset = queryset.filter(created_by_ai=created_by_ai.lower() == 'true')
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='add-exercise')
    def add_exercise(self, request, pk=None):
        """
        Add an exercise to this workout.
        
        Expected data:
        {
            "exercise_id": 1,
            "sets": 3,
            "reps": 12,
            "duration_seconds": null,
            "rest_time": 60,
            "order": 5,
            "notes": "Focus on form"
        }
        """
        user_workout = self.get_object()
        serializer = UserExerciseSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user_workout=user_workout)
            # Recalculate workout estimates
            user_workout.calculate_estimates()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """Mark a workout as active"""
        user_workout = self.get_object()
        user_workout.is_active = True
        user_workout.save()
        
        serializer = self.get_serializer(user_workout)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        """Mark a workout as inactive"""
        user_workout = self.get_object()
        user_workout.is_active = False
        user_workout.save()
        
        serializer = self.get_serializer(user_workout)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='recalculate-estimates')
    def recalculate_estimates(self, request, pk=None):
        """Recalculate estimated duration and calories"""
        user_workout = self.get_object()
        user_workout.calculate_estimates()
        
        serializer = self.get_serializer(user_workout)
        return Response(serializer.data)


class UserExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing exercises within user workouts.
    
    list: Get all exercises for a specific workout
    retrieve: Get details of a specific exercise
    create: Add an exercise to a workout
    update: Update exercise parameters
    destroy: Remove an exercise from a workout
    """
    serializer_class = UserExerciseSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = UserExercise.objects.filter(
            user_workout__user=user
        ).select_related('exercise', 'user_workout')
        
        # Filter by workout
        workout_id = self.request.query_params.get('workout', None)
        if workout_id:
            queryset = queryset.filter(user_workout_id=workout_id)
        
        return queryset
    
    def perform_create(self, serializer):
        user_exercise = serializer.save()
        # Recalculate workout estimates
        user_exercise.user_workout.calculate_estimates()
    
    def perform_update(self, serializer):
        user_exercise = serializer.save()
        # Recalculate workout estimates
        user_exercise.user_workout.calculate_estimates()
    
    def perform_destroy(self, instance):
        workout = instance.user_workout
        instance.delete()
        # Recalculate workout estimates
        workout.calculate_estimates()


class WorkoutProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking workout completion and progress.
    
    list: Get all workout progress records for the current user
    retrieve: Get details of a specific progress record
    create: Log a completed workout session
    update: Update a progress record
    destroy: Delete a progress record
    """
    permission_classes = [IsActiveUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkoutProgressCreateSerializer
        return WorkoutProgressSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = WorkoutProgress.objects.filter(
            user_workout__user=user
        ).select_related('user_workout')
        
        # Filter by workout
        workout_id = self.request.query_params.get('workout', None)
        if workout_id:
            queryset = queryset.filter(user_workout_id=workout_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(completed_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(completed_at__date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get workout statistics for the current user.
        """
        user = request.user
        progress_records = WorkoutProgress.objects.filter(user_workout__user=user)
        
        total_workouts = progress_records.count()
        total_calories = progress_records.aggregate(
            total=django_models.Sum('actual_calories')
        )['total'] or 0
        total_duration = progress_records.aggregate(
            total=django_models.Sum('actual_duration')
        )['total'] or 0
        avg_rating = progress_records.filter(rating__isnull=False).aggregate(
            avg=django_models.Avg('rating')
        )['avg'] or 0
        avg_completion = progress_records.aggregate(
            avg=django_models.Avg('completion_percentage')
        )['avg'] or 0
        
        return Response({
            'total_workouts_completed': total_workouts,
            'total_calories_burned': round(total_calories, 2),
            'total_duration_minutes': total_duration,
            'average_rating': round(avg_rating, 2),
            'average_completion_percentage': round(avg_completion, 2)
        })