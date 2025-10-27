from .models import User

def get_details_for_ai(user_id):
    try:
        user = User.objects.get(id=user_id)
        gender = user.gender
        age = user.age
        date_of_birth = user.date_of_birth
        if age is None and date_of_birth is not None:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        height_cm = user.height_cm
        weight_kg = user.weight_kg
        goal = user.goal
        activity_level = user.activity_level
        coach_type = user.coach_type.behavior if user.coach_type else None
        preferred_workout_time = user.preferred_workout_time
        preferred_workout_days = [day.name for day in user.preferred_workout_days.all()]
        
        context = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "gender": gender,
            "age": age,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "goal": goal,
            "activity_level": activity_level,
            "coach_type": coach_type,
            "preferred_workout_time": preferred_workout_time,
            "preferred_workout_days": preferred_workout_days,
        }

        return context
    except User.DoesNotExist:
        return None