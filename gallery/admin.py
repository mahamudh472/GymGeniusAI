from django.contrib import admin
from .models import UserGallery
from unfold.admin import ModelAdmin


@admin.register(UserGallery)
class UserGalleryAdmin(ModelAdmin):
    list_display = ['user', 'image_type', 'ai_detected', 'uploaded_at']
    list_filter = ['image_type', 'ai_detected', 'uploaded_at']
    search_fields = ['user__email']
    ordering = ['-uploaded_at']
    raw_id_fields = ['user']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
