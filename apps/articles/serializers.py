from rest_framework import serializers
from .models import Article, WorkoutVideo

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'image', 'category', 'created_by', 'created_at']


class WorkoutVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkoutVideo
        fields = ['id', 'video_url', 'title', 'description', 'duration_minutes', 'created_at']