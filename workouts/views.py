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
    CompleteCustomRoutineExerciseSerializer, CustomRoutineExerciseCompletionSerializer,
    DailyProgressSerializer
)
from accounts.permissions import IsActiveUser

class UserWorkoutListAPIView(generics.ListAPIView):
    queryset = UserWorkout.objects.all()
    serializer_class = UserWorkoutListSerializer
    permission_classes = [IsActiveUser]

    @extend_schema(
        summary="List user workouts",
        description="Get a list of all workouts for the authenticated user. Can be filtered by difficulty level.",
        parameters=[
            OpenApiParameter(
                name='difficulty',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter workouts by difficulty level',
                enum=['Beginner', 'Intermediate', 'Advanced']
            )
        ],
        responses={
            200: UserWorkoutListSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
        serializer = CompleteExerciseSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
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
                activity_data = ActivitySerializer(activity, context={'request': request}).data
            
            return Response({
                'message': 'Exercise marked as completed',
                'workout_progress': WorkoutProgressSerializer(workout_progress, context={'request': request}).data,
                'all_completed': all_completed,
                'activity_created': activity_created,
                'activity': activity_data,
                'completion_percentage': workout_progress.completion_percentage,
                'completed_exercises': len(workout_progress.completed_exercises),
                'total_exercises': user_workout.user_exercises.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to track workout progress.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        
        try:
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
                'workout_progress': WorkoutProgressSerializer(workout_progress, context={'request': request}).data,
                'workout_name': user_workout.name,
                'total_exercises': user_workout.user_exercises.count(),
                'completed_exercises': len(workout_progress.completed_exercises),
                'completion_percentage': workout_progress.completion_percentage,
                'all_completed': workout_progress.completion_percentage >= 100.0
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve workout progress.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        serializer = CustomRoutineSerializer(custom_routine, context={'request': request})
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
        serializer = CustomRoutineSerializer(custom_routine, context={'request': request})
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
        
        try:
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
                # Store the order of the deleted exercise
                deleted_order = existing_exercise.order
                
                # Remove the exercise
                existing_exercise.delete()
                
                # Reorder remaining exercises to fill the gap
                remaining_exercises = CustomRoutineExercise.objects.filter(
                    custom_routine=custom_routine,
                    order__gt=deleted_order
                ).order_by('order')
                
                # Decrease the order of all exercises after the deleted one
                for exercise_to_update in remaining_exercises:
                    exercise_to_update.order -= 1
                    exercise_to_update.save()
                
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
                exercise_data = CustomRoutineExerciseSerializer(new_exercise, context={'request': request}).data
            
            # Return updated custom routine
            custom_routine.refresh_from_db()
            return Response({
                'message': message,
                'action': action,
                'exercise': exercise_data,
                'custom_routine': CustomRoutineSerializer(custom_routine, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to toggle exercise in custom routine.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        try:
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
                'completion': CustomRoutineExerciseCompletionSerializer(completion, context={'request': request}).data,
                'activity': ActivitySerializer(activity, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to complete custom routine exercise.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class DailyProgressView(APIView):
    """
    Get daily progress including workout completion percentage, calories burned,
    total training time, and activities for a specific date.
    """
    permission_classes = [IsActiveUser]
    
    @extend_schema(
        summary="Get daily progress",
        description="Get daily progress summary including workout completion percentage, calories burned, total training time, and activities. If no date is provided, returns progress for today.",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Date for which to get progress (YYYY-MM-DD format). Defaults to today if not provided.',
                examples=[
                    OpenApiExample(
                        'Today',
                        value=timezone.now().date().isoformat()
                    ),
                    OpenApiExample(
                        'Specific Date',
                        value='2025-11-30'
                    )
                ]
            )
        ],
        responses={
            200: DailyProgressSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid date format'}
                }
            }
        }
    )
    def get(self, request):
        """Get daily progress for a specific date"""
        from datetime import datetime, timedelta
        
        # Parse date parameter or use today
        date_param = request.query_params.get('date')
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Please use YYYY-MM-DD format.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()
        
        try:
            user = request.user
            
            # Get the latest workout created on or before the target date
            # This represents the workout that was supposed to be done on that day
            latest_workout = UserWorkout.objects.filter(
                user=user,
                created_at__date__lte=target_date,
                is_active=True
            ).order_by('-created_at').first()
            
            # Initialize progress data
            progress_percentage = 0.0
            workout_details = None
            
            if latest_workout:
                # Get workout progress for the target date
                workout_progress = WorkoutProgress.objects.filter(
                    user_workout=latest_workout,
                    completed_at__date=target_date
                ).first()
                
                if workout_progress:
                    progress_percentage = workout_progress.completion_percentage
                    workout_details = {
                        'workout_id': latest_workout.id,
                        'workout_name': latest_workout.name,
                        'total_exercises': latest_workout.user_exercises.count(),
                        'completed_exercises': len(workout_progress.completed_exercises),
                        'estimated_duration': latest_workout.estimated_duration,
                        'estimated_calories': latest_workout.estimated_calories,
                    }
                else:
                    # No progress recorded for this workout on this date
                    workout_details = {
                        'workout_id': latest_workout.id,
                        'workout_name': latest_workout.name,
                        'total_exercises': latest_workout.user_exercises.count(),
                        'completed_exercises': 0,
                        'estimated_duration': latest_workout.estimated_duration,
                        'estimated_calories': latest_workout.estimated_calories,
                    }
            
            # Get all activities for the target date
            activities = Activity.objects.filter(
                user=user,
                created_at__date=target_date
            ).order_by('-created_at')
            
            # Calculate total calories burned and training time from activities
            total_calories = sum(activity.calories for activity in activities)
            total_training_time = sum(activity.duration for activity in activities)
            
            # Prepare response data
            response_data = {
                'date': target_date,
                'progress_percentage': progress_percentage,
                'calories_burned': total_calories,
                'total_training_time': total_training_time,
                'activities': ActivitySerializer(activities, many=True, context={'request': request}).data,
            }
            
            if workout_details:
                response_data['workout_details'] = workout_details
            
            # Return response data directly without wrapping in DailyProgressSerializer
            # since the data is already properly formatted
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve daily progress.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class WorkoutRecommendationView(generics.ListAPIView):
    """
    Retrieve a workout recommendation for the authenticated user based on their profile.
    """
    serializer_class = UserWorkoutListSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        user = self.request.user
        # Simple recommendation logic based on user's goal and activity level
        queryset = UserWorkout.objects.filter(is_active=True)

        if user.goal == 'weight_loss':
            queryset = queryset.filter(difficulty__in=['beginner', 'intermediate'])
        elif user.goal == 'muscle_gain':
            queryset = queryset.filter(difficulty__in=['intermediate', 'advanced'])
        elif user.goal == 'endurance':
            queryset = queryset.filter(difficulty__in=['beginner', 'advanced'])

        if user.activity_level == 'sedentary':
            queryset = queryset.filter(estimated_duration__lte=30)
        elif user.activity_level == 'active':
            queryset = queryset.filter(estimated_duration__gte=30)

        return queryset.order_by('?').prefetch_related('user_exercises__exercise')