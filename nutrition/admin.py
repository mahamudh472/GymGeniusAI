from django.contrib import admin
from .models import MealCategory, Meal, UserMealPlan, UserUploadedMeal
from unfold.admin import ModelAdmin

@admin.register(MealCategory)
class MealCategoryAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_per_page = 50


@admin.register(Meal)
class MealAdmin(ModelAdmin):
    list_display = ['title', 'category', 'calories', 'cook_time_min', 'ai_rating']
    list_filter = ['category']
    search_fields = ['title', 'ingredients']
    raw_id_fields = ['category']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(UserMealPlan)
class UserMealPlanAdmin(ModelAdmin):
    list_display = ['user', 'meal', 'date', 'meal_type']
    list_filter = ['meal_type', 'date']
    search_fields = ['user__email', 'meal__title']
    ordering = ['-date']
    raw_id_fields = ['user', 'meal']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'meal', 'meal__category')


@admin.register(UserUploadedMeal)
class UserUploadedMealAdmin(ModelAdmin):
    list_display = ['user', 'meal_name', 'estimated_calories', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    raw_id_fields = ['user']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
