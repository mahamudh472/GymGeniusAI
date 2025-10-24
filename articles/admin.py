from django.contrib import admin
from .models import AdminUser, Article


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'role']
    list_filter = ['role']
    search_fields = ['email']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
