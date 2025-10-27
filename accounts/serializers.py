from rest_framework import serializers
from .models import Coach, User, WeekDay
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class WeekDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDay
        fields = ['id', 'name']

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'password', 'password2']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data
    

class UserSerializer(serializers.ModelSerializer):
    preferred_workout_days = WeekDaySerializer(many=True, read_only=True)
    preferred_workout_day_ids = serializers.PrimaryKeyRelatedField(
        queryset=WeekDay.objects.all(),
        write_only=True,
        many=True,
        source='preferred_workout_days'
    )
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 
                  'first_name', 'last_name', 'gender', 
                  'age', 'date_of_birth', 'height_cm', 
                  'weight_kg', 'goal', 'activity_level', 
                  'coach_type', 'preferred_workout_time', 
                  'preferred_workout_days', 'preferred_workout_day_ids', 'joined_at']
    


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError("User account is not verified.")

        return data

class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['id', 'name', 'behavior']