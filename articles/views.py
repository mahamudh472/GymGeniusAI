from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from .models import Article, WorkoutVideo
from .serializers import ArticleSerializer, WorkoutVideoSerializer
from rest_framework.permissions import IsAdminUser

class ArticleListView(ListAPIView):
    """API view to list all articles"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleCreateView(CreateAPIView):
    """API view to create a new article"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ArticleDetailView(RetrieveAPIView):
    """API view to retrieve an article by ID"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'id'

class WorkoutVideoListView(ListAPIView):
    """API view to list all workout videos"""
    queryset = WorkoutVideo.objects.all()
    serializer_class = WorkoutVideoSerializer

class WorkoutVideoDetailView(RetrieveAPIView):
    """API view to retrieve a workout video by ID"""
    queryset = WorkoutVideo.objects.all()
    serializer_class = WorkoutVideoSerializer
    lookup_field = 'id'
