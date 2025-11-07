from rest_framework import serializers
from .models import UserGallery

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = ['id', 'user', 'image', 'image_type', 'ai_detected', 'ai_summary', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at']
