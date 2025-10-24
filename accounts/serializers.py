from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'gender', 'age', 'height_cm', 'weight_kg', 'goal', 'activity_level', 'coach_type', 'joined_at']