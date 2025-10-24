# Custom User Model - Implementation Guide

## Overview
The custom `User` model extends Django's `AbstractUser` and uses **email** as the primary authentication field instead of username.

---

## 🔑 Key Features

### Authentication
- **Username Field**: `email` (unique, required)
- **Primary Key**: UUID (auto-generated)
- **Password**: Inherited from AbstractUser (hashed)
- **Verification**: `is_verified` boolean field

### Profile Fields
```python
# Basic Info
- phone_number: Optional phone contact
- is_verified: Email/phone verification status
- gender: male/female/other
- age: Integer

# Physical Metrics
- height_cm: Float (height in centimeters)
- weight_kg: Float (weight in kilograms)

# Fitness Profile
- goal: weight_loss, muscle_gain, maintenance, endurance
- activity_level: sedentary, light, moderate, active, very_active
- coach_type: Custom coaching preference

# Subscription
- subscription_id: Links to active subscription

# Timestamps
- joined_at: Auto-set on creation
- last_login: Updated on each login
```

---

## 💻 Usage Examples

### Creating a User

```python
from accounts.models import User

# Method 1: Using create_user (recommended - hashes password)
user = User.objects.create_user(
    username='john_doe',  # Still required in REQUIRED_FIELDS
    email='john@example.com',
    password='secure_password_123',
    phone_number='+1234567890',
    gender='male',
    age=25,
    height_cm=175.0,
    weight_kg=70.5,
    goal='muscle_gain',
    activity_level='moderate'
)

# Method 2: For superusers
superuser = User.objects.create_superuser(
    username='admin',
    email='admin@gymgenius.com',
    password='admin_password'
)
```

### Authenticating Users

```python
from django.contrib.auth import authenticate, login

# Authenticate by email
user = authenticate(
    request,
    username='john@example.com',  # Use email here
    password='secure_password_123'
)

if user is not None:
    login(request, user)
    print(f"Welcome {user.email}!")
else:
    print("Invalid credentials")
```

### Querying Users

```python
# Get user by email
user = User.objects.get(email='john@example.com')

# Filter by fitness goal
weight_loss_users = User.objects.filter(goal='weight_loss')

# Active verified users
active_users = User.objects.filter(is_verified=True, is_active=True)

# Users with active subscriptions
subscribed_users = User.objects.filter(
    subscriptions__is_active=True
).distinct()
```

### Updating User Profile

```python
user = User.objects.get(email='john@example.com')

# Update fitness profile
user.weight_kg = 68.0
user.goal = 'maintenance'
user.activity_level = 'active'
user.save()

# Or use update()
User.objects.filter(id=user.id).update(
    weight_kg=68.0,
    goal='maintenance'
)
```

---

## 🔐 OTP Implementation Example

```python
from accounts.models import User, OTP
from django.utils import timezone
from datetime import timedelta
import random

def generate_otp(user, purpose='login'):
    """Generate a 6-digit OTP for user"""
    code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=10)
    
    otp = OTP.objects.create(
        user=user,
        code=code,
        purpose=purpose,
        expires_at=expires_at
    )
    
    # TODO: Send OTP via email/SMS
    print(f"OTP for {user.email}: {code}")
    return otp

def verify_otp(user, code, purpose='login'):
    """Verify OTP code"""
    try:
        otp = OTP.objects.get(
            user=user,
            code=code,
            purpose=purpose,
            is_used=False
        )
        
        if otp.is_valid():
            otp.is_used = True
            otp.save()
            
            # Mark user as verified if signup OTP
            if purpose == 'signup':
                user.is_verified = True
                user.save()
            
            return True
        return False
    except OTP.DoesNotExist:
        return False
```

---

## 📊 Subscription Management

```python
from accounts.models import User, SubscriptionPlan, UserSubscription
from datetime import date, timedelta

# Create a subscription plan
plan = SubscriptionPlan.objects.create(
    name='Premium Monthly',
    price=29.99,
    duration_days=30,
    features={
        'ai_coach': True,
        'meal_plans': True,
        'workout_videos': True,
        'community_access': True
    },
    is_active=True
)

# Subscribe a user
def subscribe_user(user, plan):
    """Create a subscription for user"""
    start_date = date.today()
    end_date = start_date + timedelta(days=plan.duration_days)
    
    subscription = UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        is_active=True,
        payment_status='completed',
        transaction_id=f'TXN-{user.id}-{start_date}'
    )
    
    user.subscription_id = plan.id
    user.save()
    
    return subscription

# Check active subscription
def has_active_subscription(user):
    """Check if user has an active subscription"""
    return UserSubscription.objects.filter(
        user=user,
        is_active=True,
        end_date__gte=date.today()
    ).exists()
```

---

## 🎯 Related Models Access

```python
user = User.objects.get(email='john@example.com')

# Access related models using related_name
otps = user.otps.all()
subscriptions = user.subscriptions.filter(is_active=True)
conversations = user.ai_conversations.all()
notifications = user.notifications.filter(is_read=False)
workouts = user.workout_progress.all()
meals = user.meal_plans.filter(date=date.today())
challenges = user.user_challenges.filter(completed=False)
gallery = user.gallery_images.all()
feedback = user.feedback_reports.all()

# Leaderboard (one-to-one)
try:
    leaderboard_entry = user.leaderboard
    print(f"Rank: {leaderboard_entry.rank}, XP: {leaderboard_entry.xp_points}")
except:
    print("User not on leaderboard yet")
```

---

## 🔄 Migration Commands

```bash
# Create migrations after model changes
python manage.py makemigrations accounts

# Apply migrations
python manage.py migrate accounts

# Check migration status
python manage.py showmigrations accounts

# Rollback if needed
python manage.py migrate accounts 0001_initial
```

---

## 🚨 Important Notes

### Username Field
- Even though email is the USERNAME_FIELD, the `username` field still exists (from AbstractUser)
- It's in REQUIRED_FIELDS for createsuperuser command
- You can make it optional or auto-generate it if desired

### Password Management
- Always use `create_user()` or `set_password()` to hash passwords
- Never store plain text passwords
- Use Django's built-in password validators

### UUID Primary Key
- UUIDs are auto-generated on creation
- Better for distributed systems and security
- Slightly slower than integer PKs but more secure

### Email as Username
- Ensures email uniqueness
- Better UX for users (one less thing to remember)
- Standard in modern applications

---

## 🎨 Admin Interface

The custom UserAdmin extends Django's BaseUserAdmin with additional fieldsets:

```python
# Access at: http://127.0.0.1:8000/admin/accounts/user/

# Fieldsets include:
1. Personal info (inherited)
2. Permissions (inherited)
3. Important dates (inherited)
4. Profile Information (custom)
   - phone_number, is_verified, gender, age, height_cm, weight_kg
5. Fitness Goals (custom)
   - goal, activity_level, coach_type, subscription_id
```

---

## 📱 API Considerations

When building REST APIs:

```python
# Serializer example (using Django REST Framework)
from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number',
            'gender', 'age', 'height_cm', 'weight_kg',
            'goal', 'activity_level', 'coach_type',
            'is_verified', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
```

---

## ✅ Testing

```python
from django.test import TestCase
from accounts.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            gender='male',
            age=25
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_email_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')
    
    def test_uuid_primary_key(self):
        self.assertIsNotNone(self.user.id)
        self.assertEqual(len(str(self.user.id)), 36)  # UUID length
```

---

## 🎓 Best Practices

1. **Always use email for authentication** in your views/APIs
2. **Hash passwords** with `set_password()` or `create_user()`
3. **Verify emails** before allowing full access
4. **Update last_login** on each successful authentication
5. **Use transactions** when updating related models
6. **Index frequently queried fields** if needed
7. **Validate fitness data** (e.g., weight > 0, age > 0)

---

**Status:** ✅ Custom User Model Fully Implemented and Ready to Use
