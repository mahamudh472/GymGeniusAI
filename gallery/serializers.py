from rest_framework import serializers
from .models import UserGallery

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = ['id', 'user', 'image_url', 'image_type', 'ai_detected', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at']
