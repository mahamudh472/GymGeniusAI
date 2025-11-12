from rest_framework import generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from django.utils import timezone
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseSerializer, UserWorkoutListSerializer,
    UserWorkoutSerializer, UserExerciseSerializer, WorkoutProgressSerializer,
    CompleteExerciseSerializer, ActivitySerializer
)
from accounts.permissions import IsActiveUser

class UserWorkoutListAPIView(generics.ListAPIView):
    queryset = UserWorkout.objects.all()
    serializer_class = UserWorkoutListSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user).prefetch_related('user_exercises__exercise')
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.capitalize())
        return queryset

class UserWorkoutDetailAPIView(generics.RetrieveAPIView):
    queryset = UserWorkout.objects.all()
    serializer_class = UserWorkoutSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).prefetch_related('user_exercises__exercise')

from .utils import generate_workouts_for_user

@api_view(['GET', 'POST'])
@permission_classes([IsActiveUser])
def test(request):
    print(generate_workouts_for_user(user=request.user))
    return Response({"message": "Test successful"})


class TrackWorkoutProgressView(APIView):
    """
    Track workout progress by marking exercises as completed.
    When all exercises are completed, create an Activity record.
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        serializer = CompleteExerciseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user_workout_id = serializer.validated_data['user_workout_id']
        user_exercise_id = serializer.validated_data['user_exercise_id']
        
        # Validate that the workout belongs to the user
        user_workout = get_object_or_404(UserWorkout, id=user_workout_id, user=user)
        
        # Validate that the exercise belongs to the workout
        user_exercise = get_object_or_404(UserExercise, id=user_exercise_id, user_workout=user_workout)
        
        # Get or create WorkoutProgress for today's session
        today = timezone.now().date()
        workout_progress, created = WorkoutProgress.objects.filter(
            user_workout=user_workout,
            completed_at__date=today
        ).first(), False
        
        if not workout_progress:
            workout_progress = WorkoutProgress.objects.create(
                user_workout=user_workout,
                completed_exercises=[],
                completion_percentage=0.0
            )
            created = True
        
        # Add the exercise to completed list if not already there
        if user_exercise_id not in workout_progress.completed_exercises:
            workout_progress.completed_exercises.append(user_exercise_id)
            
            # Calculate completion percentage
            total_exercises = user_workout.user_exercises.count()
            completed_count = len(workout_progress.completed_exercises)
            workout_progress.completion_percentage = (completed_count / total_exercises) * 100 if total_exercises > 0 else 0
            
            # Save additional notes if provided
            if serializer.validated_data.get('notes'):
                existing_notes = workout_progress.notes or ""
                workout_progress.notes = f"{existing_notes}\nExercise {user_exercise.exercise.name}: {serializer.validated_data['notes']}"
            
            workout_progress.save()
        
        # Check if all exercises are completed
        all_completed = workout_progress.completion_percentage >= 100.0
        activity_created = False
        activity_data = None
        
        if all_completed:
            # Calculate actual duration and calories
            actual_duration = user_workout.estimated_duration or 0
            actual_calories = user_workout.estimated_calories or 0.0
            
            # Update workout progress with actual metrics
            if not workout_progress.actual_duration:
                workout_progress.actual_duration = actual_duration
            if not workout_progress.actual_calories:
                workout_progress.actual_calories = float(actual_calories)
            workout_progress.save()
            
            # Create Activity record
            activity = Activity.objects.create(
                user=user,
                name=user_workout.name,
                duration=actual_duration,
                calories=float(actual_calories)
            )
            activity_created = True
            activity_data = ActivitySerializer(activity).data
        
        return Response({
            'message': 'Exercise marked as completed',
            'workout_progress': WorkoutProgressSerializer(workout_progress).data,
            'all_completed': all_completed,
            'activity_created': activity_created,
            'activity': activity_data,
            'completion_percentage': workout_progress.completion_percentage,
            'completed_exercises': len(workout_progress.completed_exercises),
            'total_exercises': user_workout.user_exercises.count()
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        """Get current workout progress for a specific workout"""
        user_workout_id = request.query_params.get('user_workout_id')
        
        if not user_workout_id:
            return Response({
                'error': 'user_workout_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_workout = get_object_or_404(UserWorkout, id=user_workout_id, user=request.user)
        
        # Get today's progress
        today = timezone.now().date()
        workout_progress = WorkoutProgress.objects.filter(
            user_workout=user_workout,
            completed_at__date=today
        ).first()
        
        if not workout_progress:
            return Response({
                'message': 'No progress recorded for today',
                'workout_id': user_workout_id,
                'workout_name': user_workout.name,
                'total_exercises': user_workout.user_exercises.count(),
                'completed_exercises': 0,
                'completion_percentage': 0.0
            }, status=status.HTTP_200_OK)
        
        return Response({
            'workout_progress': WorkoutProgressSerializer(workout_progress).data,
            'workout_name': user_workout.name,
            'total_exercises': user_workout.user_exercises.count(),
            'completed_exercises': len(workout_progress.completed_exercises),
            'completion_percentage': workout_progress.completion_percentage,
            'all_completed': workout_progress.completion_percentage >= 100.0
        }, status=status.HTTP_200_OK)


class ActivityListView(generics.ListAPIView):
    """
    List all activities for the authenticated user.
    """
    serializer_class = ActivitySerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by('-created_at')