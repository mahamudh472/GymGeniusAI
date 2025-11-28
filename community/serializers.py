from rest_framework import serializers
from .models import ForumPost

class ForumPostSerializer(serializers.ModelSerializer):
    """Serializer for ForumPost model"""
    user_name = serializers.SerializerMethodField()
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else obj.user.username

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user_name', 'content', 'likes', 'views', 'user_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'likes', 'views', 'created_at', 'updated_at']