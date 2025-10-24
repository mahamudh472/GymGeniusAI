from rest_framework import serializers
from .models import AIConversation, ConversationMessage

class AIConversationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = ['id', 'user', 'prompt', 'response', 'created_at']

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIConversationDetailSerializer(many=True, read_only=True)
    class Meta:
        model = AIConversation
        fields = ['id', 'user', 'created_at', 'messages']
