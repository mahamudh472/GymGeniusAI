from django.db import models
from accounts.models import User


class MealCategory(models.Model):
    """Categories for meals"""
    name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'meal_categories'
        verbose_name = 'Meal Category'
        verbose_name_plural = 'Meal Categories'
    
    def __str__(self):
        return self.name


class Meal(models.Model):
    """Meal plans and recipes"""
    title = models.CharField(max_length=150)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(MealCategory, on_delete=models.CASCADE, related_name='meals')
    ingredients = models.TextField(blank=True, null=True)
    preparation = models.TextField(blank=True, null=True)
    cook_time_min = models.IntegerField(blank=True, null=True, help_text="Cooking time in minutes")
    calories = models.FloatField(blank=True, null=True)
    macros = models.JSONField(default=dict, help_text="Macronutrients (protein, carbs, fats)")
    micros = models.JSONField(default=dict, help_text="Micronutrients (vitamins, minerals)")
    ai_rating = models.FloatField(blank=True, null=True, help_text="AI health rating")
    health_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'meals'
        verbose_name = 'Meal'
        verbose_name_plural = 'Meals'
    
    def __str__(self):
        return self.title


class UserMealPlan(models.Model):
    """User's meal planning schedule"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(max_length=50,
                                 choices=[
                                     ('breakfast', 'Breakfast'),
                                     ('lunch', 'Lunch'),
                                     ('dinner', 'Dinner'),
                                     ('snack', 'Snack'),
                                 ])
    
    class Meta:
        db_table = 'user_meal_plans'
        verbose_name = 'User Meal Plan'
        verbose_name_plural = 'User Meal Plans'
        ordering = ['date', 'meal_type']
    
    def __str__(self):
        return f"{self.user.email} - {self.meal_type} - {self.date}"


class UserUploadedMeal(models.Model):
    """User uploaded meal images with AI analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_meals')
    image_url = models.URLField(max_length=255)
    ai_analysis = models.JSONField(default=dict, help_text="AI nutrition analysis")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_uploaded_meals'
        verbose_name = 'User Uploaded Meal'
        verbose_name_plural = 'User Uploaded Meals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
