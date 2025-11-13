from rest_framework import generics, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress, Activity,
    CustomRoutine, CustomRoutineExercise, CustomRoutineExerciseCompletion
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseSerializer, UserWorkoutListSerializer,
    UserWorkoutSerializer, UserExerciseSerializer, WorkoutProgressSerializer,
    CompleteExerciseSerializer, ActivitySerializer, CustomRoutineSerializer,
    CustomRoutineExerciseSerializer, ToggleExerciseSerializer,
    CompleteCustomRoutineExerciseSerializer, CustomRoutineExerciseCompletionSerializer
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



class TrackWorkoutProgressView(APIView):
    """
    Track workout progress by marking exercises as completed.
    When all exercises are completed, create an Activity record.
    """
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Mark exercise as completed",
        description="Mark an exercise in a workout as completed. Tracks progress and creates an Activity record when all exercises are completed.",
        request=CompleteExerciseSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Exercise marked as completed'},
                    'workout_progress': {'type': 'object'},
                    'all_completed': {'type': 'boolean', 'example': False},
                    'activity_created': {'type': 'boolean', 'example': False},
                    'activity': {'type': 'object', 'nullable': True},
                    'completion_percentage': {'type': 'number', 'example': 33.33},
                    'completed_exercises': {'type': 'integer', 'example': 1},
                    'total_exercises': {'type': 'integer', 'example': 3}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid input'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Complete Exercise Example',
                value={
                    'user_workout_id': 1,
                    'user_exercise_id': 5,
                    'actual_sets': 3,
                    'actual_reps': 12,
                    'actual_duration': 300,
                    'notes': 'Felt great, increased weight'
                },
                request_only=True
            )
        ]
    )
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
    
    @extend_schema(
        summary="Get workout progress",
        description="Get the current workout progress for a specific workout for today's session.",
        parameters=[
            OpenApiParameter(
                name='user_workout_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID of the user workout to get progress for',
                examples=[
                    OpenApiExample(
                        'Example workout ID',
                        value=1
                    )
                ]
            )
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'workout_progress': {'type': 'object'},
                    'workout_name': {'type': 'string', 'example': 'Morning Strength Training'},
                    'total_exercises': {'type': 'integer', 'example': 5},
                    'completed_exercises': {'type': 'integer', 'example': 2},
                    'completion_percentage': {'type': 'number', 'example': 40.0},
                    'all_completed': {'type': 'boolean', 'example': False}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'user_workout_id is required'}
                }
            }
        }
    )
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


class ExerciseListView(generics.ListAPIView):
    """
    List all available exercises that users can add to their custom routine.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by muscle group if provided
        muscle_group = self.request.query_params.get('muscle_group', None)
        if muscle_group:
            queryset = queryset.filter(muscle_group__icontains=muscle_group)
        
        # Filter by difficulty if provided
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset


class CustomRoutineView(APIView):
    """
    Get or update the user's custom routine.
    Custom routine is automatically created when first accessed.
    """
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Get custom routine",
        description="Get the user's custom routine with all exercises. Creates a new custom routine if one doesn't exist.",
        responses={
            200: CustomRoutineSerializer,
        }
    )
    def get(self, request):
        """Get user's custom routine"""
        # Get or create custom routine for the user
        custom_routine, created = CustomRoutine.objects.get_or_create(
            user=request.user,
            defaults={'name': 'My Custom Routine'}
        )
        
        serializer = CustomRoutineSerializer(custom_routine)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Update custom routine details",
        description="Update the name and description of the user's custom routine.",
        request=inline_serializer(
            name='CustomRoutineUpdateSerializer',
            fields={
                'name': serializers.CharField(required=False),
                'description': serializers.CharField(required=False, allow_blank=True),
            }
        ),
        responses={
            200: CustomRoutineSerializer,
        }
    )
    def patch(self, request):
        """Update custom routine name/description"""
        custom_routine, created = CustomRoutine.objects.get_or_create(
            user=request.user,
            defaults={'name': 'My Custom Routine'}
        )
        
        if 'name' in request.data:
            custom_routine.name = request.data['name']
        if 'description' in request.data:
            custom_routine.description = request.data['description']
        
        custom_routine.save()
        serializer = CustomRoutineSerializer(custom_routine)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ToggleCustomRoutineExerciseView(APIView):
    """
    Toggle an exercise in the user's custom routine.
    If the exercise exists, it will be removed. If not, it will be added.
    """
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Toggle exercise in custom routine",
        description="Add or remove an exercise from the user's custom routine. If the exercise is already in the routine, it will be removed. Otherwise, it will be added.",
        request=ToggleExerciseSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Exercise added to custom routine'},
                    'action': {'type': 'string', 'enum': ['added', 'removed'], 'example': 'added'},
                    'exercise': {'type': 'object'},
                    'custom_routine': {'type': 'object'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid input'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Exercise not found'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Toggle Exercise Example',
                value={'exercise_id': 5},
                request_only=True
            )
        ]
    )
    def post(self, request):
        """Toggle exercise in custom routine"""
        serializer = ToggleExerciseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        exercise_id = serializer.validated_data['exercise_id']
        
        # Validate that the exercise exists
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Get or create custom routine
        custom_routine, created = CustomRoutine.objects.get_or_create(
            user=request.user,
            defaults={'name': 'My Custom Routine'}
        )
        
        # Check if exercise already exists in custom routine
        existing_exercise = CustomRoutineExercise.objects.filter(
            custom_routine=custom_routine,
            exercise=exercise
        ).first()
        
        if existing_exercise:
            # Remove the exercise
            existing_exercise.delete()
            action = 'removed'
            message = f'Exercise "{exercise.name}" removed from custom routine'
            exercise_data = None
        else:
            # Add the exercise
            # Get the next order number
            max_order = CustomRoutineExercise.objects.filter(
                custom_routine=custom_routine
            ).aggregate(max_order=django_models.Max('order'))['max_order']
            next_order = (max_order or 0) + 1
            
            new_exercise = CustomRoutineExercise.objects.create(
                custom_routine=custom_routine,
                exercise=exercise,
                order=next_order
            )
            action = 'added'
            message = f'Exercise "{exercise.name}" added to custom routine'
            exercise_data = CustomRoutineExerciseSerializer(new_exercise).data
        
        # Return updated custom routine
        custom_routine.refresh_from_db()
        return Response({
            'message': message,
            'action': action,
            'exercise': exercise_data,
            'custom_routine': CustomRoutineSerializer(custom_routine).data
        }, status=status.HTTP_200_OK)


class CustomRoutineExercisesListView(generics.ListAPIView):
    """
    List all exercises in the user's custom routine.
    """
    serializer_class = CustomRoutineExerciseSerializer
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="List custom routine exercises",
        description="Get a list of all exercises in the user's custom routine.",
        responses={
            200: CustomRoutineExerciseSerializer(many=True),
        }
    )
    def get_queryset(self):
        # Get or create custom routine
        custom_routine, created = CustomRoutine.objects.get_or_create(
            user=self.request.user,
            defaults={'name': 'My Custom Routine'}
        )
        
        return CustomRoutineExercise.objects.filter(
            custom_routine=custom_routine
        ).select_related('exercise').order_by('order', 'added_at')


class CompleteCustomRoutineExerciseView(APIView):
    """
    Mark a custom routine exercise as completed.
    Creates an Activity record for the completed exercise.
    """
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Complete custom routine exercise",
        description="Mark a custom routine exercise as completed. Automatically creates an Activity record for tracking.",
        request=CompleteCustomRoutineExerciseSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Exercise completed successfully'},
                    'completion': {'type': 'object'},
                    'activity': {'type': 'object'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid input'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Custom routine exercise not found'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Complete Exercise Example',
                value={
                    'custom_routine_exercise_id': 1,
                    'actual_sets': 3,
                    'actual_reps': 12,
                    'duration_minutes': 5,
                    'notes': 'Felt great!',
                    'difficulty_rating': 'moderate'
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """Complete a custom routine exercise"""
        serializer = CompleteCustomRoutineExerciseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        custom_routine_exercise_id = serializer.validated_data['custom_routine_exercise_id']
        
        # Get the custom routine exercise and verify it belongs to the user
        custom_routine_exercise = get_object_or_404(
            CustomRoutineExercise,
            id=custom_routine_exercise_id,
            custom_routine__user=user
        )
        
        # Calculate calories burned
        actual_sets = serializer.validated_data['actual_sets']
        actual_reps = serializer.validated_data.get('actual_reps')
        
        if actual_reps:
            calories_burned = actual_sets * actual_reps * custom_routine_exercise.exercise.calories_per_rep
        else:
            # Use default reps if not provided
            calories_burned = actual_sets * (custom_routine_exercise.reps or 10) * custom_routine_exercise.exercise.calories_per_rep
        
        # Create completion record
        completion = CustomRoutineExerciseCompletion.objects.create(
            user=user,
            custom_routine_exercise=custom_routine_exercise,
            actual_sets=actual_sets,
            actual_reps=actual_reps,
            actual_duration_seconds=serializer.validated_data.get('actual_duration_seconds'),
            duration_minutes=serializer.validated_data['duration_minutes'],
            calories_burned=calories_burned,
            notes=serializer.validated_data.get('notes', ''),
            difficulty_rating=serializer.validated_data.get('difficulty_rating')
        )
        
        # Create Activity record
        activity = Activity.objects.create(
            user=user,
            name=custom_routine_exercise.exercise.name,
            duration=serializer.validated_data['duration_minutes'],
            calories=float(calories_burned)
        )
        
        return Response({
            'message': 'Exercise completed successfully',
            'completion': CustomRoutineExerciseCompletionSerializer(completion).data,
            'activity': ActivitySerializer(activity).data
        }, status=status.HTTP_200_OK)


class CustomRoutineExerciseCompletionHistoryView(generics.ListAPIView):
    """
    List completion history for custom routine exercises.
    """
    serializer_class = CustomRoutineExerciseCompletionSerializer
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Get custom routine exercise completion history",
        description="Get a list of all completed custom routine exercises for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name='exercise_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter by specific exercise ID'
            ),
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter completions from the last N days'
            )
        ],
        responses={
            200: CustomRoutineExerciseCompletionSerializer(many=True),
        }
    )
    def get_queryset(self):
        queryset = CustomRoutineExerciseCompletion.objects.filter(
            user=self.request.user
        ).select_related('custom_routine_exercise__exercise')
        
        # Filter by exercise if provided
        exercise_id = self.request.query_params.get('exercise_id')
        if exercise_id:
            queryset = queryset.filter(custom_routine_exercise__exercise_id=exercise_id)
        
        # Filter by days if provided
        days = self.request.query_params.get('days')
        if days:
            from datetime import timedelta
            from django.utils import timezone
            cutoff_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(completed_at__gte=cutoff_date)
        
        return queryset.order_by('-completed_at')