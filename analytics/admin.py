from django.contrib import admin
from .models import FeedbackReport, AnalyticsLog
from unfold.admin import ModelAdmin


@admin.register(FeedbackReport)
class FeedbackReportAdmin(ModelAdmin):
    list_display = ['user', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__email', 'message']
    ordering = ['-created_at']


@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(ModelAdmin):
    list_display = ['event_type', 'user', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'user__email']
    ordering = ['-created_at']
