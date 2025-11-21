from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RankViewSet, ActivityTypeViewSet, UserRankViewSet,
    PointTransactionViewSet, LeaderboardView, UserStatsView,
    DailyCheckInView, AwardPointsView, WeeklyLeaderboardHistoryView,
    RankHistoryView, UserStreakView
)

app_name = 'gamification'

router = DefaultRouter()
router.register(r'ranks', RankViewSet, basename='rank')
router.register(r'activities', ActivityTypeViewSet, basename='activity')
router.register(r'user-ranks', UserRankViewSet, basename='user-rank')
router.register(r'transactions', PointTransactionViewSet, basename='transaction')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
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
]
