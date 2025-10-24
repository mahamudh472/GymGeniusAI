from django.contrib import admin
from .models import FeedbackReport, AnalyticsLog


@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__email', 'message']
    ordering = ['-created_at']


@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'user__email']
    ordering = ['-created_at']
