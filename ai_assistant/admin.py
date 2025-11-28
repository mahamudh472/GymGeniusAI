from django.contrib import admin
from .models import AIConversation, ConversationMessage
from unfold.admin import ModelAdmin


class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 1
    fields = [ 'message', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(AIConversation)
class AIConversationAdmin(ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__email', 'prompt', 'response']
    ordering = ['-created_at']
    
    inlines = [ConversationMessageInline]

