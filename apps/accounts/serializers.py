from rest_framework import serializers
from .models import Coach, User, WeekDay, SubscriptionPlan
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class WeekDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDay
        fields = ['id', 'name']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password']
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        return user

    

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data
    

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    preferred_workout_days = WeekDaySerializer(many=True, read_only=True)
    preferred_workout_day_ids = serializers.PrimaryKeyRelatedField(
        queryset=WeekDay.objects.all(),
        write_only=True,
        many=True,
        source='preferred_workout_days'
    )
    rank = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'avatar',
                  'full_name', 'gender',
                  'age', 'date_of_birth', 'height_cm',
                  'weight_kg', 'goal', 'activity_level',
                  'coach_type', 'preferred_workout_time', 'rank',
                  'preferred_workout_days', 'preferred_workout_day_ids', 'joined_at']
    
    def get_rank(self, obj):
        if hasattr(obj, 'user_rank') and obj.user_rank.current_rank:
            return {
                'id': obj.user_rank.current_rank.id,
                'name': obj.user_rank.current_rank.name,
                'level': obj.user_rank.current_rank.level,
                'color_code': obj.user_rank.current_rank.color_code
            }
        return None

    


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

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
