from django.contrib import admin
from .models import Article
from unfold.admin import ModelAdmin


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
