from unfold.admin import ModelAdmin
from .models import FAQ, ContactOption, Favorite
from django.contrib import admin
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