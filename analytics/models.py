from django.db import models
from accounts.models import User


class FeedbackReport(models.Model):
    """User feedback and reports"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_reports')
    message = models.TextField()
    type = models.CharField(max_length=20,
                          choices=[
                              ('feedback', 'Feedback'),
                              ('bug', 'Bug Report'),
                              ('feature', 'Feature Request'),
                              ('complaint', 'Complaint'),
                          ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback_reports'
        verbose_name = 'Feedback Report'
        verbose_name_plural = 'Feedback Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.created_at.strftime('%Y-%m-%d')}"


class AnalyticsLog(models.Model):
    """Analytics event logging"""
    event_type = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_logs')
    meta = models.JSONField(default=dict, help_text="Additional event metadata")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_logs'
        verbose_name = 'Analytics Log'
        verbose_name_plural = 'Analytics Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        user_email = self.user.email if self.user else 'Anonymous'
        return f"{self.event_type} - {user_email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
