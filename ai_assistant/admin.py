from django.contrib import admin
from .models import AIConversation
from unfold.admin import ModelAdmin


@admin.register(AIConversation)
class AIConversationAdmin(ModelAdmin):
    list_display = ['user', 'created_at', 'prompt_preview']
    search_fields = ['user__email', 'prompt', 'response']
    ordering = ['-created_at']
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt Preview'
