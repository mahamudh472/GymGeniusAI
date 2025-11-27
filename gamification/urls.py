from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RankViewSet, ActivityTypeViewSet, UserRankViewSet,
    PointTransactionViewSet, LeaderboardView, UserStatsView,
    DailyCheckInView, AwardPointsView, WeeklyLeaderboardHistoryView,
    RankHistoryView, UserStreakView, ChallengeViewSet,
    StartChallengeView, CompleteChallengeExerciseView,
    UserChallengeProgressView, ClaimChallengeRewardView
)

app_name = 'gamification'

router = DefaultRouter()
router.register(r'ranks', RankViewSet, basename='rank')
router.register(r'activities', ActivityTypeViewSet, basename='activity')
router.register(r'user-ranks', UserRankViewSet, basename='user-rank')
router.register(r'transactions', PointTransactionViewSet, basename='transaction')
router.register(r'challenges', ChallengeViewSet, basename='challenge')

urlpatterns = [
    # Leaderboard
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/history/', WeeklyLeaderboardHistoryView.as_view(), name='leaderboard-history'),
    
    # User stats and info
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('streak/', UserStreakView.as_view(), name='user-streak'),
    path('rank-history/', RankHistoryView.as_view(), name='rank-history'),
    
    # Actions
    path('checkin/', DailyCheckInView.as_view(), name='daily-checkin'),
    path('award-points/', AwardPointsView.as_view(), name='award-points'),
    
    # Challenges - Must come BEFORE router URLs to avoid conflicts
    path('challenges/start/', StartChallengeView.as_view(), name='start-challenge'),
    path('challenges/complete-exercise/', CompleteChallengeExerciseView.as_view(), name='complete-challenge-exercise'),
    path('challenges/my-progress/', UserChallengeProgressView.as_view(), name='user-challenge-progress'),
    path('challenges/claim-reward/', ClaimChallengeRewardView.as_view(), name='claim-challenge-reward'),
    
    # Router URLs - Must come LAST
    path('', include(router.urls)),
]
