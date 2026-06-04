from rest_framework import serializers
from apps.nutrition.models import UserUploadedMeal, TemporaryMealUpload

class UserUploadedMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUploadedMeal
        fields = [
            'id',
            'meal_name',
            'estimated_calories',
            'image',
            'ai_analysis',
            'macronutrients',
            'micronutrients',
            'improvements',
            'created_at',
        ]


class TemporaryMealUploadSerializer(serializers.ModelSerializer):
    """Serializer for temporary meal uploads"""
    class Meta:
        model = TemporaryMealUpload
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_image(self, value):
        """Validate the uploaded image"""
        if not value:
            raise serializers.ValidationError("Image file is required.")
            
        # Check file size (e.g., max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image file size cannot exceed 10MB.")
        
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in valid_extensions:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(valid_extensions)}"
            )
        
        return value
    
    def create(self, validated_data):
        """Override create to ensure proper file handling"""
        return TemporaryMealUpload.objects.create(**validated_data)