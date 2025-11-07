from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Favorite, FAQ, ContactOption
from drf_spectacular.utils import extend_schema_field, OpenApiTypes

# Import your actual content serializers
from workouts.serializers import UserWorkoutListSerializer
from articles.serializers import ArticleSerializer
# from videos.serializers import VideoSerializer

FAVORITE_SERIALIZERS = {
    'userworkout': UserWorkoutListSerializer,
    'article': ArticleSerializer,
    # 'video': VideoSerializer,
}


class FavoriteSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True, required=False)
    object_id = serializers.IntegerField(write_only=True, required=False)
    type = serializers.SerializerMethodField(read_only=True)
    object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Favorite
        fields = [
            'id',
            'content_type',
            'object_id',
            'type',
            'object',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'type', 'object']

    # --- for GET ---
    def get_type(self, obj):
        """Return the type of favorited object (e.g. 'workout', 'article')."""
        return obj.content_type.model
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_object(self, obj):
        """Return serialized representation of the favorited object."""
        target = obj.content_object
        if not target:
            return None

        serializer_class = FAVORITE_SERIALIZERS.get(obj.content_type.model)
        if serializer_class:
            return serializer_class(target).data
        return {"id": target.id}

    # --- for POST ---
    def create(self, validated_data):
        """Handle creation/deletion of a Favorite (toggle behavior)."""
        user = self.context['request'].user
        model_name = validated_data.get('content_type')
        object_id = validated_data.get('object_id')

        if not model_name or not object_id:
            raise serializers.ValidationError("Both 'content_type' and 'object_id' are required.")

        try:
            content_type = ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist:
            valid_types = ", ".join(ContentType.objects.values_list('model', flat=True))
            raise serializers.ValidationError(f"Invalid content type: {model_name}. Valid types are: {valid_types}")

        # Validate that the object exists
        model_class = content_type.model_class()
        if not model_class.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError(f"Object with id {object_id} does not exist for type {model_name}.")

        favorite, created = Favorite.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id
        )
        
        if not created:
            # Already exists, so remove it
            favorite.delete()
            # Return a deleted instance for response handling
            favorite.id = None
        
        return favorite

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactOption
        fields = ['id', 'name', 'icon', 'link', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
