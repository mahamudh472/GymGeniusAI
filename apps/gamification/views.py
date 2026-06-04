from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    Rank, UserRank, PointTransaction, ActivityType,
    WeeklyLeaderboard, RankHistory, UserStreak, Challenge, UserChallengeProgress
)
from .serializers import (
    RankSerializer, UserRankSerializer, PointTransactionSerializer,
    ActivityTypeSerializer, WeeklyLeaderboardSerializer, RankHistorySerializer,
    UserStreakSerializer, LeaderboardResponseSerializer, UserStatsSerializer,
    AwardPointsSerializer, CheckInResponseSerializer, ChallengeSerializer,
    UserChallengeProgressSerializer, StartChallengeSerializer,
    CompleteChallengeExerciseSerializer, ClaimChallengeRewardSerializer
)
from .utils import (
    get_leaderboard_for_user, get_user_stats, award_points,
    process_daily_checkin, get_available_activities, get_all_ranks,
    get_or_create_user_rank
)
from apps.workouts.models import Activity


class RankViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing ranks.
    Only read operations are allowed.
    """
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all ranks",
        description="Get a list of all available ranks in the system"
    )
    def list(self, request, *args, **kwargs):
        ranks = get_all_ranks()
        return Response({
            'success': True,
            'data': ranks
        })


class ActivityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing activity types.
    Only read operations are allowed.
    """
    queryset = ActivityType.objects.filter(is_active=True)
    serializer_class = ActivityTypeSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all activities",
        description="Get a list of all activities that can earn points"
    )
    def list(self, request, *args, **kwargs):
        activities = get_available_activities()
        return Response({
            'success': True,
            'data': activities
        })


class UserRankViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user ranks.
    """
    serializer_class = UserRankSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserRank.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Get current user rank",
        description="Get the authenticated user's current rank information"
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's rank info"""
        user_rank = get_or_create_user_rank(request.user)
        serializer = self.get_serializer(user_rank)
        return Response({
            'success': True,
            'data': serializer.data
        })


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing point transactions.
    """
    serializer_class = PointTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PointTransaction.objects.filter(
            user=self.request.user
        ).select_related('activity_type').order_by('-created_at')
    
    @extend_schema(
        summary="List user's point transactions",
        description="Get a list of all point transactions for the authenticated user"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LeaderboardView(APIView):
    """
    View for getting the leaderboard.
    Shows only users in the same rank as the current user.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get leaderboard",
        description="Get the leaderboard showing users in the same rank as the current user",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of users to return (default: 50)',
                required=False
            )
        ],
        responses={200: LeaderboardResponseSerializer}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        leaderboard_data = get_leaderboard_for_user(request.user, limit=limit, request=request)
        
        return Response({
            'success': True,
            'data': leaderboard_data
        })


class UserStatsView(APIView):
    """
    View for getting comprehensive user statistics.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user statistics",
        description="Get comprehensive statistics for the authenticated user including rank, points, streak, and history",
        responses={200: UserStatsSerializer}
    )
    def get(self, request):
        stats = get_user_stats(request.user)
        
        return Response({
            'success': True,
            'data': stats
        })


class DailyCheckInView(APIView):
    """
    View for processing daily check-ins.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Daily check-in",
        description="Process daily check-in for the authenticated user. Awards points and updates streak.",
        responses={200: CheckInResponseSerializer}
    )
    def post(self, request):
        success, message, points = process_daily_checkin(request.user)
        
        # Get updated streak info
        streak = UserStreak.objects.filter(user=request.user).first()
        
        response_data = {
            'success': success,
            'message': message,
            'points_awarded': points,
            'current_streak': streak.current_streak if streak else 0,
            'total_check_ins': streak.total_check_ins if streak else 0
        }
        
        return Response(response_data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


class AwardPointsView(APIView):
    """
    View for awarding points to users.
    This should typically be called by other parts of the system.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Award points",
        description="Award points to the authenticated user for completing an activity",
        request=AwardPointsSerializer,
        responses={200: {'type': 'object', 'properties': {
            'success': {'type': 'boolean'},
            'message': {'type': 'string'},
            'points_awarded': {'type': 'integer'}
        }}}
    )
    def post(self, request):
        serializer = AwardPointsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        activity_code = serializer.validated_data['activity_code']
        metadata = serializer.validated_data.get('metadata', {})
        custom_points = serializer.validated_data.get('custom_points')
        
        success, message, points = award_points(
            request.user,
            activity_code,
            metadata=metadata,
            custom_points=custom_points
        )
        
        response_data = {
            'success': success,
            'message': message,
            'points_awarded': points
        }
        
        return Response(response_data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


class WeeklyLeaderboardHistoryView(APIView):
    """
    View for getting historical weekly leaderboards.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get weekly leaderboard history",
        description="Get historical weekly leaderboard entries for the authenticated user",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of weeks to return (default: 10)',
                required=False
            )
        ],
        responses={200: WeeklyLeaderboardSerializer(many=True)}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        history = WeeklyLeaderboard.objects.filter(
            user=request.user
        ).select_related('rank', 'old_rank').order_by('-week_start')[:limit]
        
        serializer = WeeklyLeaderboardSerializer(history, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class RankHistoryView(APIView):
    """
    View for getting rank change history.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get rank history",
        description="Get the history of rank changes for the authenticated user",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of entries to return (default: 20)',
                required=False
            )
        ],
        responses={200: RankHistorySerializer(many=True)}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        
        history = RankHistory.objects.filter(
            user=request.user
        ).select_related('old_rank', 'new_rank').order_by('-changed_at')[:limit]
        
        serializer = RankHistorySerializer(history, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class UserStreakView(APIView):
    """
    View for getting user streak information.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user streak",
        description="Get the check-in streak information for the authenticated user",
        responses={200: UserStreakSerializer}
    )
    def get(self, request):
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        serializer = UserStreakSerializer(streak)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing challenges.
    Users can view available challenges and filter by type.
    """
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all challenges",
        description="Get a list of all active challenges. Can be filtered by challenge type and availability.",
        parameters=[
            OpenApiParameter(
                name='challenge_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by challenge type (DAILY or WEEKLY)',
                required=False,
                enum=['DAILY', 'WEEKLY']
            ),
            OpenApiParameter(
                name='available_only',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Show only currently available challenges',
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Filter by challenge type
        challenge_type = request.query_params.get('challenge_type')
        if challenge_type:
            queryset = queryset.filter(challenge_type=challenge_type.upper())
        
        # Filter by availability
        available_only = request.query_params.get('available_only', '').lower() == 'true'
        if available_only:
            now = timezone.now()
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        
        queryset = queryset.order_by('-start_date')
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'data': serializer.data
        })
    
    @extend_schema(
        summary="Get challenge details",
        description="Get detailed information about a specific challenge"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Check if user has started this challenge
        user_progress = UserChallengeProgress.objects.filter(
            user=request.user,
            challenge=instance
        ).first()
        
        data = serializer.data
        data['user_progress'] = UserChallengeProgressSerializer(user_progress).data if user_progress else None
        
        return Response({
            'success': True,
            'data': data
        })


class StartChallengeView(APIView):
    """
    View for starting a challenge.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Start a challenge",
        description="Start participating in a challenge. Creates a progress tracking record.",
        request=StartChallengeSerializer,
        responses={
            200: UserChallengeProgressSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    def post(self, request):
        serializer = StartChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
        
        # Check if challenge is available
        if not challenge.is_available():
            return Response({
                'success': False,
                'error': 'This challenge is not currently available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already started this challenge
        existing_progress = UserChallengeProgress.objects.filter(
            user=request.user,
            challenge=challenge
        ).first()
        
        if existing_progress:
            return Response({
                'success': False,
                'error': 'You have already started this challenge',
                'data': UserChallengeProgressSerializer(existing_progress).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create progress record
        progress = UserChallengeProgress.objects.create(
            user=request.user,
            challenge=challenge,
            status='IN_PROGRESS',
            completed_exercises=[],
            completion_percentage=0.0
        )
        
        return Response({
            'success': True,
            'message': f'Started challenge: {challenge.name}',
            'data': UserChallengeProgressSerializer(progress).data
        }, status=status.HTTP_201_CREATED)


class CompleteChallengeExerciseView(APIView):
    """
    View for completing an exercise within a challenge.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Complete challenge exercise",
        description="Mark an exercise in a challenge as completed. Tracks progress and awards points when all exercises are completed.",
        request=CompleteChallengeExerciseSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {'type': 'object'},
                    'challenge_completed': {'type': 'boolean'},
                    'points_awarded': {'type': 'integer'}
                }
            }
        }
    )
    def post(self, request):
        serializer = CompleteChallengeExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        exercise_index = serializer.validated_data['exercise_index']
        
        # Get challenge progress
        progress = get_object_or_404(
            UserChallengeProgress,
            user=request.user,
            challenge_id=challenge_id
        )
        
        # Check if challenge is still available
        if not progress.challenge.is_available():
            # Mark as failed if expired
            if progress.status == 'IN_PROGRESS':
                progress.status = 'FAILED'
                progress.save()
            
            return Response({
                'success': False,
                'error': 'This challenge has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if challenge is already completed
        if progress.status == 'COMPLETED':
            return Response({
                'success': False,
                'error': 'Challenge already completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate exercise index
        if exercise_index >= len(progress.challenge.exercises):
            return Response({
                'success': False,
                'error': 'Invalid exercise index'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add exercise to completed list if not already completed
        if exercise_index not in progress.completed_exercises:
            progress.completed_exercises.append(exercise_index)
            
            # Calculate completion percentage
            total_exercises = len(progress.challenge.exercises)
            progress.completion_percentage = (len(progress.completed_exercises) / total_exercises) * 100
            
            # Check if all exercises are completed
            challenge_completed = progress.completion_percentage >= 100.0
            points_awarded = 0
            activity_created = False
            activity_data = None
            
            if challenge_completed:
                progress.status = 'COMPLETED'
                progress.completed_at = timezone.now()
                
                # Calculate actual metrics
                if not progress.actual_duration:
                    progress.actual_duration = progress.challenge.estimated_duration or 0
                if not progress.actual_calories:
                    progress.actual_calories = float(progress.challenge.estimated_calories or 0)
                
                # Award points
                success, message, points = progress.check_and_award_points()
                points_awarded = points
                
                # Create Activity record (same as regular workout)
                try:
                    activity = Activity.objects.create(
                        user=request.user,
                        name=f"Challenge: {progress.challenge.name}",
                        duration=progress.actual_duration,
                        calories=progress.actual_calories
                    )
                    activity_created = True
                    activity_data = {
                        'id': activity.id,
                        'name': activity.name,
                        'duration': activity.duration,
                        'calories': activity.calories,
                        'created_at': activity.created_at.isoformat()
                    }
                except Exception as e:
                    # Log error but don't fail the challenge completion
                    pass
            
            # Add notes if provided
            if serializer.validated_data.get('notes'):
                existing_notes = progress.notes or ""
                exercise_name = progress.challenge.exercises[exercise_index].get('name', f'Exercise {exercise_index + 1}')
                progress.notes = f"{existing_notes}\n{exercise_name}: {serializer.validated_data['notes']}"
            
            progress.save()
            
            response_data = {
                'success': True,
                'message': 'Exercise completed successfully' + (' - Challenge completed!' if challenge_completed else ''),
                'data': UserChallengeProgressSerializer(progress).data,
                'challenge_completed': challenge_completed,
                'points_awarded': points_awarded
            }
            
            if challenge_completed:
                response_data['activity_created'] = activity_created
                response_data['activity'] = activity_data
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': 'Exercise already completed'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserChallengeProgressView(APIView):
    """
    View for getting user's challenge progress.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user challenge progress",
        description="Get all challenge progress records for the authenticated user. Can be filtered by status.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by status',
                required=False,
                enum=['IN_PROGRESS', 'COMPLETED', 'FAILED']
            )
        ],
        responses={200: UserChallengeProgressSerializer(many=True)}
    )
    def get(self, request):
        queryset = UserChallengeProgress.objects.filter(
            user=request.user
        ).select_related('challenge').order_by('-started_at')
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        serializer = UserChallengeProgressSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'data': serializer.data
        })


class ClaimChallengeRewardView(APIView):
    """
    View for manually claiming challenge rewards (if needed).
    Normally rewards are auto-claimed when challenge is completed.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Claim challenge reward",
        description="Manually claim reward for a completed challenge (if not already claimed)",
        request=ClaimChallengeRewardSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'points_awarded': {'type': 'integer'}
                }
            }
        }
    )
    def post(self, request):
        serializer = ClaimChallengeRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        progress_id = serializer.validated_data['challenge_progress_id']
        progress = get_object_or_404(
            UserChallengeProgress,
            id=progress_id,
            user=request.user
        )
        
        success, message, points = progress.check_and_award_points()
        
        return Response({
            'success': success,
            'message': message,
            'points_awarded': points
        }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
