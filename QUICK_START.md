# Quick Start Guide - Gym Genius AI

## ✅ What's Been Implemented

All database models from your DBML schema have been successfully created and migrated!

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source env/bin/activate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser --email admin@gymgenius.com --username admin
# Enter password when prompted
```

### 3. Run Development Server
```bash
python manage.py runserver
```

### 4. Access Admin Panel
Open browser: http://127.0.0.1:8000/admin/
Login with your superuser credentials

---

## 📋 Available Models in Admin

### Users & Auth (accounts)
- ✅ Users (Custom user model)
- ✅ OTPs
- ✅ Subscription Plans
- ✅ User Subscriptions

### AI & Notifications
- ✅ AI Conversations (ai_assistant)
- ✅ Notifications (notifications)

### Workouts
- ✅ Workout Categories
- ✅ Workouts
- ✅ Workout Rounds
- ✅ Exercises
- ✅ User Workout Progress

### Nutrition
- ✅ Meal Categories
- ✅ Meals
- ✅ User Meal Plans
- ✅ User Uploaded Meals

### Community
- ✅ Communities
- ✅ Challenges
- ✅ User Challenges
- ✅ Leaderboard

### Gallery
- ✅ User Gallery

### Articles
- ✅ Admin Users
- ✅ Articles

### Analytics
- ✅ Feedback Reports
- ✅ Analytics Logs

---

## 📊 Model Relationships

```
User (accounts.User)
  ├── otps (OTP)
  ├── subscriptions (UserSubscription)
  ├── ai_conversations (AIConversation)
  ├── notifications (Notification)
  ├── workout_progress (UserWorkoutProgress)
  ├── meal_plans (UserMealPlan)
  ├── uploaded_meals (UserUploadedMeal)
  ├── created_communities (Community)
  ├── created_challenges (Challenge)
  ├── user_challenges (UserChallenge)
  ├── leaderboard (Leaderboard) [one-to-one]
  ├── gallery_images (UserGallery)
  ├── feedback_reports (FeedbackReport)
  └── analytics_logs (AnalyticsLog)

Workout
  ├── rounds (WorkoutRound)
  └── Each round has exercises (Exercise)

Meal
  └── Used in meal_plans (UserMealPlan)
```

---

## 🎯 Key Features

### Custom User Model
- **UUID primary key** for better security
- **Email-based authentication** (not username)
- **Fitness profile fields**: gender, age, height, weight, goal, activity_level
- **Built-in verification**: is_verified field
- **Subscription tracking**: subscription_id

### JSON Fields
Used for flexible data storage:
- Subscription features
- Macros and micros in meals
- AI analysis results
- Completed rounds tracking
- Analytics metadata

### Proper Relationships
- Foreign Keys with CASCADE/SET_NULL as appropriate
- Related names for reverse queries
- Unique constraints where needed
- Proper ordering and indexing

---

## 💡 Common Tasks

### Add a Workout Category
```python
from workouts.models import WorkoutCategory

category = WorkoutCategory.objects.create(
    name='Cardio',
    description='Heart-pumping cardiovascular exercises'
)
```

### Add a Meal Category
```python
from nutrition.models import MealCategory

category = MealCategory.objects.create(name='Breakfast')
```

### Create a Subscription Plan
```python
from accounts.models import SubscriptionPlan

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
```

### Register a New User
```python
from accounts.models import User

user = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='secure_password',
    phone_number='+1234567890',
    gender='male',
    age=25,
    height_cm=175.0,
    weight_kg=70.0,
    goal='muscle_gain',
    activity_level='moderate'
)
```

---

## 📁 Project Structure

```
GymGeniusAI/
├── accounts/          # User management & subscriptions
├── ai_assistant/      # AI chat functionality
├── analytics/         # Analytics & feedback
├── articles/          # Content management
├── community/         # Social features & challenges
├── gallery/           # Progress photos
├── notifications/     # User notifications
├── nutrition/         # Meal planning
├── workouts/          # Workout programs
├── GymGeniusAI/      # Project settings
├── db.sqlite3         # Database
├── manage.py
├── DATABASE_MODELS_SUMMARY.md      # Comprehensive docs
└── CUSTOM_USER_GUIDE.md            # User model guide
```

---

## 🔧 Useful Commands

```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for issues
python manage.py check

# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Shell for testing
python manage.py shell

# Show all migrations
python manage.py showmigrations
```

---

## 🎨 Admin Customizations

All models have custom admin configurations with:
- Searchable fields
- Filterable columns
- Custom list displays
- Proper ordering
- Related field lookups

---

## 📝 Next Steps

1. ✅ **Models Created** - All 24 models implemented
2. ✅ **Migrations Applied** - Database tables created
3. ✅ **Admin Registered** - All models accessible in admin
4. 🔲 **Create Superuser** - Run createsuperuser command
5. 🔲 **Add Initial Data** - Create categories, plans, etc.
6. 🔲 **Build APIs** - Django REST Framework endpoints
7. 🔲 **Add Authentication** - JWT, OTP verification
8. 🔲 **Frontend Integration** - Connect with React/Vue/etc.

---

## 📚 Documentation Files

- **DATABASE_MODELS_SUMMARY.md** - Complete model documentation
- **CUSTOM_USER_GUIDE.md** - Custom user model usage guide
- **QUICK_START.md** - This file

---

## 🎉 Status: READY FOR DEVELOPMENT!

All models are implemented, tested, and ready to use. You can now:
- Access the admin panel to add data
- Create API endpoints
- Build authentication flows
- Integrate with frontend
- Add business logic to views

**No errors detected. System is fully operational!** ✅

---

## 📞 Support

For questions about:
- **Models**: Check DATABASE_MODELS_SUMMARY.md
- **Custom User**: Check CUSTOM_USER_GUIDE.md
- **Django**: https://docs.djangoproject.com/
- **Admin**: http://127.0.0.1:8000/admin/ (after runserver)

Happy Coding! 🚀💪

