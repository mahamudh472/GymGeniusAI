from django.db import models
from accounts.models import User


class AIConversation(models.Model):
    """AI chat conversations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_conversations'
        verbose_name = 'AI Conversation'
        verbose_name_plural = 'AI Conversations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ConversationMessage(models.Model):
    """Messages within an AI conversation"""
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=50,
                              choices=[
                                  ('user', 'User'),
                                  ('ai', 'AI Assistant'),
                              ])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_messages'
        verbose_name = 'Conversation Message'
        verbose_name_plural = 'Conversation Messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.conversation.user.email} - {self.sender} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
