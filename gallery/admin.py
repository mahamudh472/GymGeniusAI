from django.contrib import admin
from .models import UserGallery


@admin.register(UserGallery)
class UserGalleryAdmin(admin.ModelAdmin):
    list_display = ['user', 'image_type', 'ai_detected', 'uploaded_at']
    list_filter = ['image_type', 'ai_detected', 'uploaded_at']
    search_fields = ['user__email']
    ordering = ['-uploaded_at']
