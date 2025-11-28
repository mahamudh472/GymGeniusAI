from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ForumPostViewSet

app_name = 'community'
router = DefaultRouter()
router.register(r'forum-posts', ForumPostViewSet, basename='forum-post')

urlpatterns = router.urls