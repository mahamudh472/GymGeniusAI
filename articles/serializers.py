from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'media_url', 'category', 'created_by', 'created_at']