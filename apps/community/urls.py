from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CommentCreateAPIView, ForumPostLikeAPIView, ForumPostViewSet,
    CommentListAPIView, CommentDetailAPIView,
    ForumPostReportAPIView, ForumCommentReportAPIView,
    UserBlockAPIView, UserUnblockAPIView, BlockedUserListAPIView
)

app_name = 'community'
router = DefaultRouter()
router.register(r'forum-posts', ForumPostViewSet, basename='forum-post')

urlpatterns = router.urls
urlpatterns += [
    path('forum-post-like/', ForumPostLikeAPIView.as_view(), name='forum-post-like'),
    path('forum-comments/<int:post_id>/', CommentListAPIView.as_view(), name='forum-comments'),
    path('forum-comment/<int:pk>/', CommentDetailAPIView.as_view(), name='forum-comment-detail'),
    path('forum-comment-create/', CommentCreateAPIView.as_view(), name='forum-comment-create'),

    # Report endpoints
    path('report-post/', ForumPostReportAPIView.as_view(), name='report-post'),
    path('report-comment/', ForumCommentReportAPIView.as_view(), name='report-comment'),

    # Block endpoints
    path('block-user/', UserBlockAPIView.as_view(), name='block-user'),
    path('unblock-user/<int:user_id>/', UserUnblockAPIView.as_view(), name='unblock-user'),
    path('blocked-users/', BlockedUserListAPIView.as_view(), name='blocked-users'),
]