from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    Rank, UserRank, PointTransaction, ActivityType,
    WeeklyLeaderboard, RankHistory, UserStreak
)
from .serializers import (
    RankSerializer, UserRankSerializer, PointTransactionSerializer,
    ActivityTypeSerializer, WeeklyLeaderboardSerializer, RankHistorySerializer,
    UserStreakSerializer, LeaderboardResponseSerializer, UserStatsSerializer,
    AwardPointsSerializer, CheckInResponseSerializer
)
from .utils import (
    get_leaderboard_for_user, get_user_stats, award_points,
    process_daily_checkin, get_available_activities, get_all_ranks,
    get_or_create_user_rank
)


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
        leaderboard_data = get_leaderboard_for_user(request.user, limit=limit)
        
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
