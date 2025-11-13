from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from .models import UserGallery
from .serializers import GalleryImageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, pagination
from rest_framework.response import Response
from django.utils.dateparse import parse_date
import django_filters.rest_framework
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from datetime import date


def calculate_upload_streak(user):
    """
    Calculate the consecutive days streak of gallery uploads for a user.
    Counts backward from today to find the last consecutive upload days.
    """
    # Get all unique dates with uploads, ordered descending
    upload_dates = UserGallery.objects.filter(user=user).dates('uploaded_at', 'day', order='DESC')
    
    if not upload_dates:
        return 0
    
    streak = 0
    current_date = date.today()
    
    for upload_date in upload_dates:
        # Check if upload is from current_date
        if upload_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Streak broken
            break
    
    return streak


class GalleryImagePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class GalleryDashboardView(GenericAPIView):
    """
    API view to provide dashboard statistics for the user's gallery images.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GalleryImageSerializer  # Add serializer_class for schema generation

    @extend_schema(
        responses={
            200: inline_serializer(
                name='GalleryDashboardResponse',
                fields={
                    'total_images': serializers.IntegerField(),
                    'images_last_week': serializers.IntegerField(),
                    'consecutive_days_streak': serializers.IntegerField(),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        total_images = UserGallery.objects.filter(user=user).count()
        
        one_week_ago = timezone.now() - timedelta(days=7)
        images_last_week = UserGallery.objects.filter(user=user, uploaded_at__gte=one_week_ago).count()
        
        streak = calculate_upload_streak(user)

        return Response({
            "total_images": total_images,
            "images_last_week": images_last_week,
            "consecutive_days_streak": streak,
        })


class GalleryImageList(ListCreateAPIView):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = GalleryImagePagination

    def get_queryset(self):
        return UserGallery.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GalleryImageFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='date')
    start_date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='lte')
    image_type = django_filters.CharFilter(field_name='image_type')

    class Meta:
        model = UserGallery
        fields = ['date', 'start_date', 'end_date', 'image_type']

class GalleryViewset(viewsets.ModelViewSet):
    queryset = UserGallery.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]
    
    filterset_class = GalleryImageFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    pagination_class = GalleryImagePagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return UserGallery.objects.filter(user=self.request.user)

class GalleryImageDetail(RetrieveAPIView):
    queryset = UserGallery.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]
