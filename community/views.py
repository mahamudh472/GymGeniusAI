from rest_framework.viewsets import ModelViewSet
from .models import ForumPost, ForumComment, ForumPostLike
from .serializers import ForumPostLikeSerializer, ForumPostSerializer, ForumCommentSerializer
from accounts.permissions import IsActiveUser
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from django.core.exceptions import PermissionDenied

class ForumPostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ForumCommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ForumPostViewSet(ModelViewSet):
    permission_classes = [IsActiveUser]
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer  
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = ForumPostPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class ForumPostLikeAPIView(GenericAPIView):
    permission_classes = [IsActiveUser]
    queryset = ForumPostLike.objects.all()
    serializer_class = ForumPostLikeSerializer   
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            if 'Like removed' in str(e.detail):
                return Response({'detail': 'Like removed.'}, status=status.HTTP_200_OK)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class CommentListAPIView(GenericAPIView):
    permission_classes = [IsActiveUser]
    serializer_class = ForumCommentSerializer
    pagination_class = ForumCommentPagination

    def get(self, request, post_id=None, *args, **kwargs):
        if post_id:
            comments = ForumComment.objects.filter(post_id=post_id).order_by('created_at')
        else:
            comments = ForumComment.objects.all().order_by('created_at')
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsActiveUser]
    queryset = ForumComment.objects.all()
    serializer_class = ForumCommentSerializer
    http_method_names = ['get', 'patch', 'delete']

    def perform_update(self, serializer):
        serializer.save()

class CommentCreateAPIView(GenericAPIView):
    permission_classes = [IsActiveUser]
    serializer_class = ForumCommentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
