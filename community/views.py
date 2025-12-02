from rest_framework.viewsets import ModelViewSet
from .models import ForumPost
from .serializers import ForumPostSerializer


class ForumPostViewSet(ModelViewSet):
    """ViewSet for managing forum posts"""
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer  
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
