from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from .models import Article
from .serializers import ArticleSerializer
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