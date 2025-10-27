from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from .models import UserGallery
from .serializers import GalleryImageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from django.utils.dateparse import parse_date
import django_filters.rest_framework

class GalleryImageList(ListCreateAPIView):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return UserGallery.objects.filter(user=self.request.user)

class GalleryImageDetail(RetrieveAPIView):
    queryset = UserGallery.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]
