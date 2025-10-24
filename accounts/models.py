from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone

class Coach(models.Model):
    name = models.CharField(max_length=150)
    behavior = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model without mandatory username"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Fitness profile fields
    gender = models.CharField(max_length=20, blank=True, null=True,
                              choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height_cm = models.FloatField(blank=True, null=True)
    weight_kg = models.FloatField(blank=True, null=True)
    goal = models.CharField(max_length=50, blank=True, null=True,
                            choices=[
                                ('weight_loss', 'Weight Loss'),
                                ('try_ai_coach', 'Try AI Coach'),
                                ('gain_endurance', 'Gain Endurance'),
                            ])
    activity_level = models.CharField(max_length=50, blank=True, null=True,
                                      choices=[
                                          ('beginner', 'Beginner'),
                                          ('intermediate', 'Intermediate'),
                                          ('advanced', 'Advanced')
                                      ])
    coach_type = models.ForeignKey(Coach, on_delete=models.SET_NULL, blank=True, null=True)
    subscription_id = models.IntegerField(blank=True, null=True)
    preferred_workout_time = models.TimeField(blank=True, null=True, help_text="Preferred time of day for workouts")
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # nothing else required for createsuperuser

    class Meta:
        db_table = 'users'

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
