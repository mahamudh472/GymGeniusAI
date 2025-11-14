from django.contrib import admin
from .models import Article, WorkoutVideo
from unfold.admin import ModelAdmin


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']

@admin.register(WorkoutVideo)
class WorkoutVideoAdmin(ModelAdmin):
    list_display = ['title', 'duration_minutes', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    