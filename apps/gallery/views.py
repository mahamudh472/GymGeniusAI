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
        parameters=[
            inline_serializer(
                name='GalleryDashboardQueryParams',
                fields={
                    'month': serializers.IntegerField(
                        required=False,
                        min_value=1,
                        max_value=12,
                        help_text="Month number (1-12). Defaults to current month if omitted."
                    ),
                    'year': serializers.IntegerField(
                        required=False,
                        min_value=1900,
                        help_text="Year (e.g., 2025). Defaults to current year if omitted."
                    ),
                }
            )
        ],
        responses={
            200: inline_serializer(
                name='GalleryDashboardResponse',
                fields={
                    'total_images': serializers.IntegerField(),
                    'images_last_week': serializers.IntegerField(),
                    'consecutive_days_streak': serializers.IntegerField(),
                    'date_image_types': serializers.DictField(
                        child=serializers.ListField(
                            child=serializers.CharField()
                        )
                    ),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            total_images = UserGallery.objects.filter(user=user).count()

            month, year = request.query_params.get('month'), request.query_params.get('year')
            if month is not None:
                month = int(month)
            else:
                month = timezone.now().month
            if year is not None:
                year = int(year)
            else:
                year = timezone.now().year

            month_data = UserGallery.objects.filter(
                user=user,
                uploaded_at__year=year,
                uploaded_at__month=month
            )
            month_data = UserGallery.objects.filter(
                user=user,
                uploaded_at__year=year,
                uploaded_at__month=month
            ).values('uploaded_at__date', 'image_type')
            date_image_types = {}

            choices = dict(UserGallery._meta.get_field('image_type').choices)

            for item in month_data:
                date_str = item['uploaded_at__date'].isoformat()
                raw_type = item['image_type']
                image_type = choices.get(raw_type)
                if not raw_type:
                    continue

                if date_str not in date_image_types:
                    date_image_types[date_str] = set()

                date_image_types[date_str].add(image_type)                
            one_week_ago = timezone.now() - timedelta(days=7)
            images_last_week = UserGallery.objects.filter(user=user, uploaded_at__gte=one_week_ago).count()
            
            latest_images = UserGallery.objects.filter(user=user).order_by('-uploaded_at')[:2]

            streak = calculate_upload_streak(user)

            # get the first (earliest) uploaded image and the last (most recent) uploaded image
            first_obj = UserGallery.objects.filter(user=user).order_by('uploaded_at').first()
            last_obj = UserGallery.objects.filter(user=user).order_by('-uploaded_at').first()

            before = GalleryImageSerializer(first_obj, context={"request": request}).data if first_obj else None
            after = GalleryImageSerializer(last_obj, context={"request": request}).data if last_obj else None

            if before == after:
                after = None

            progress_days_count = (last_obj.uploaded_at.date() - first_obj.uploaded_at.date()).days + 1 if first_obj and last_obj else 0

            return Response({
                "total_images": total_images,
                "images_last_week": images_last_week,
                "consecutive_days_streak": streak,
                "date_image_types": date_image_types,
                "latest_images": GalleryImageSerializer(latest_images, many=True, context={"request": request}).data,
                "before": before,
                "after": after,
                "progress_days_count": progress_days_count
            })
        except Exception as e:
            return Response({
                "error": "Failed to retrieve gallery statistics.",
                "detail": str(e)
            }, status=500)



class GalleryImageList(ListCreateAPIView):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = GalleryImagePagination

    def get_queryset(self):
        return UserGallery.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "error": "Failed to upload image.",
                "detail": str(e)
            }, status=500)

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
