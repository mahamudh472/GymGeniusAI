import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with additional fitness-related fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Fitness profile fields
    gender = models.CharField(max_length=20, blank=True, null=True, 
                            choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height_cm = models.FloatField(blank=True, null=True, help_text="Height in centimeters")
    weight_kg = models.FloatField(blank=True, null=True, help_text="Weight in kilograms")
    goal = models.CharField(max_length=50, blank=True, null=True,
                          choices=[
                              ('weight_loss', 'Weight Loss'),
                              ('muscle_gain', 'Muscle Gain'),
                              ('maintenance', 'Maintenance'),
                              ('endurance', 'Endurance'),
                          ])
    activity_level = models.CharField(max_length=50, blank=True, null=True,
                                    choices=[
                                        ('sedentary', 'Sedentary'),
                                        ('light', 'Light'),
                                        ('moderate', 'Moderate'),
                                        ('active', 'Active'),
                                        ('very_active', 'Very Active'),
                                    ])
    coach_type = models.CharField(max_length=50, blank=True, null=True)
    subscription_id = models.IntegerField(blank=True, null=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email


class OTP(models.Model):
    """OTP for authentication purposes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=50, 
                              choices=[
                                  ('signup', 'Signup'),
                                  ('login', 'Login'),
                                  ('password_reset', 'Password Reset'),
                              ])
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
    
    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at


class SubscriptionPlan(models.Model):
    """Subscription plans available"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text="Duration in days")
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class UserSubscription(models.Model):
    """User subscription records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    payment_status = models.CharField(max_length=20,
                                     choices=[
                                         ('pending', 'Pending'),
                                         ('completed', 'Completed'),
                                         ('failed', 'Failed'),
                                         ('refunded', 'Refunded'),
                                     ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
