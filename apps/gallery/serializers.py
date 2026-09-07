from rest_framework import serializers
from .models import UserGallery

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = ['id', 'user', 'image', 'image_type', 'ai_detected', 'ai_summary', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at', 'image_type', 'ai_detected', 'ai_summary']


class ComparisonImageSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = UserGallery
        fields = ['id', 'image', 'image_type', 'date', 'uploaded_at', 'ai_detected', 'ai_summary']

    def get_date(self, obj):
        if obj.uploaded_at:
            return obj.uploaded_at.date().isoformat()
        return None


class ComparisonTypeSerializer(serializers.Serializer):
    first = ComparisonImageSerializer(allow_null=True)
    last = ComparisonImageSerializer(allow_null=True)


class GalleryComparisonResponseSerializer(serializers.Serializer):
    front = ComparisonTypeSerializer()
    back = ComparisonTypeSerializer()
    side = ComparisonTypeSerializer()
