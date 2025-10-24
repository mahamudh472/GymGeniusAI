from django.contrib import admin
from .models import MealCategory, Meal, UserMealPlan, UserUploadedMeal


@admin.register(MealCategory)
class MealCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'calories', 'cook_time_min', 'ai_rating']
    list_filter = ['category']
    search_fields = ['title', 'ingredients']


@admin.register(UserMealPlan)
class UserMealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal', 'date', 'meal_type']
    list_filter = ['meal_type', 'date']
    search_fields = ['user__email', 'meal__title']
    ordering = ['-date']


@admin.register(UserUploadedMeal)
class UserUploadedMealAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
