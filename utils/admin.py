from unfold.admin import ModelAdmin
from .models import FAQ, ContactOption, Favorite, Notification, PrivacyPolicy
from django.contrib import admin


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    pass
    # list_display = ['user', 'title', 'is_read', 'created_at']
    # list_filter = ['is_read', 'created_at']
    # search_fields = ['user__email', 'title', 'message']
    # ordering = ['-created_at']


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ['question', 'created_at', 'updated_at']
    search_fields = ['question', 'answer']

@admin.register(ContactOption)
class ContactOptionAdmin(ModelAdmin):
    list_display = ['name', 'link', 'created_at', 'updated_at']
    search_fields = ['name', 'link']

@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'created_at']
    search_fields = ['user__username', 'content_type__model']

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(ModelAdmin):
    list_display = ['updated_at']
    readonly_fields = ['updated_at']
