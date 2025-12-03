from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import  CommentCreateAPIView, ForumPostLikeAPIView, ForumPostViewSet, CommentListAPIView, CommentDetailAPIView

app_name = 'community'
router = DefaultRouter()
router.register(r'forum-posts', ForumPostViewSet, basename='forum-post')

urlpatterns = router.urls
urlpatterns += [
    path('forum-post-like/', ForumPostLikeAPIView.as_view(), name='forum-post-like'),
    path('forum-comments/<int:post_id>/', CommentListAPIView.as_view(), name='forum-comments'),
    path('forum-comment/<int:pk>/', CommentDetailAPIView.as_view(), name='forum-comment-detail'),
    path('forum-comment-create/', CommentCreateAPIView.as_view(), name='forum-comment-create'),

]