from rest_framework import serializers
from .models import ForumPost, ForumComment, ForumPostLike

class ForumPostSerializer(serializers.ModelSerializer):
    """Serializer for ForumPost model"""
    user_name = serializers.SerializerMethodField()
    comments = serializers.IntegerField(source='comments.count', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else obj.user.username

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user_name', 'avatar', 'content', 'likes', 'comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'avatar', 'likes', 'comments', 'created_at', 'updated_at']

class ForumCommentSerializer(serializers.ModelSerializer):
    """Serializer for ForumComment model"""
    user_name = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else obj.user.username

    class Meta:
        model = ForumComment
        fields = [
            'id', 'post', 'user_name', 'avatar', 'content', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'avatar', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        request = self.context.get('request', None)
        if request and request.method in ['PATCH', 'PUT']:
            comment = self.instance
            if comment.user != request.user:
                raise serializers.ValidationError("You do not have permission to edit this comment.")
        return attrs
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and request.method in ['PATCH', 'PUT']:
            fields.pop('post', None)  
        return fields

class ForumPostLikeSerializer(serializers.ModelSerializer):
    """Serializer for ForumPostLike model"""
    class Meta:
        model = ForumPostLike
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, attrs):
        request = self.context.get('request', None)
        post = attrs.get('post') or (request.data.get('post') if request else None)
        user = attrs.get('user') or (request.user if request else None)

        if post is None or user is None:
            return attrs

        existing_like = ForumPostLike.objects.filter(post=post, user=user).first()
        if existing_like:
            # Unlike: remove the like object and decrement post.likes (never below 0)
            existing_like.delete()
            post = ForumPost.objects.get(id=post.id)
            post.likes = max(0, post.likes - 1)
            post.save()
            # stop creation of a new like (we already removed it)
            raise serializers.ValidationError({"detail": "Like removed."})

        # Not liked yet: increment post.likes (creation will create the ForumPostLike)
        post = ForumPost.objects.get(id=post.id)
        post.likes += 1
        post.save()

        return attrs