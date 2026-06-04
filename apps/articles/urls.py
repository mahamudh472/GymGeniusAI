from django.urls import path
from .views import ArticleListView, ArticleCreateView, ArticleDetailView, WorkoutVideoListView, WorkoutVideoDetailView

urlpatterns = [
    path('', ArticleListView.as_view(), name='article-list'),
    path('create/', ArticleCreateView.as_view(), name='article-create'),
    path('<int:id>/', ArticleDetailView.as_view(), name='article-detail'),
    path('workout-videos/', WorkoutVideoListView.as_view(), name='workoutvideo-list'),
    path('workout-videos/<int:id>/', WorkoutVideoDetailView.as_view(), name='workoutvideo-detail'),
]