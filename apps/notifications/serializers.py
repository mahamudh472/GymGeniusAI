from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'message',
            'notification_type',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']
        
    def create(self, validated_data):
        """Create a new notification for the user."""
        user = self.context['request'].user
        notification = Notification.objects.create(user=user, **validated_data)
        return notification