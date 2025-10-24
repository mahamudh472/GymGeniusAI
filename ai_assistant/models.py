from django.db import models
from accounts.models import User


class AIConversation(models.Model):
    """AI chat conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_conversations'
        verbose_name = 'AI Conversation'
        verbose_name_plural = 'AI Conversations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
