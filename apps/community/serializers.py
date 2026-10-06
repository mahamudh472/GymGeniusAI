from rest_framework import serializers
from .models import ForumPost, ForumComment, ForumPostLike, ForumPostReport, ForumCommentReport, UserBlock

class ForumPostSerializer(serializers.ModelSerializer):
    """Serializer for ForumPost model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    comments = serializers.IntegerField(source='comments.count', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user_id', 'user_name', 'avatar', 'content', 'likes', 'comments', 'is_owner', 'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'user_id', 'is_owner', 'is_liked', 'avatar', 'likes', 'comments', 'created_at', 'updated_at']
    
    def get_is_owner(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.user == request.user
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return ForumPostLike.objects.filter(post=obj, user=request.user).exists()
        return False

class ForumCommentSerializer(serializers.ModelSerializer):
    """Serializer for ForumComment model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumComment
        fields = [
            'id', 'post', 'user_name', 'avatar', 'content', 'is_owner',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'avatar', 'is_owner', 'created_at', 'updated_at']
    def get_is_owner(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.user == request.user
        return False
    
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


class ForumPostReportSerializer(serializers.ModelSerializer):
    """Serializer for ForumPostReport model"""
    reported_by_name = serializers.CharField(source='reported_by.full_name', read_only=True)

    class Meta:
        model = ForumPostReport
        fields = [
            'id', 'post', 'reported_by_name', 'reason', 'description',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'reported_by_name', 'status', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        post = attrs.get('post')
        if request and post:
            if post.user == request.user:
                raise serializers.ValidationError("You cannot report your own post.")
            if ForumPostReport.objects.filter(post=post, reported_by=request.user).exists():
                raise serializers.ValidationError("You have already reported this post.")
        return attrs


class ForumCommentReportSerializer(serializers.ModelSerializer):
    """Serializer for ForumCommentReport model"""
    reported_by_name = serializers.CharField(source='reported_by.full_name', read_only=True)

    class Meta:
        model = ForumCommentReport
        fields = [
            'id', 'comment', 'reported_by_name', 'reason', 'description',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'reported_by_name', 'status', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        comment = attrs.get('comment')
        if request and comment:
            if comment.user == request.user:
                raise serializers.ValidationError("You cannot report your own comment.")
            if ForumCommentReport.objects.filter(comment=comment, reported_by=request.user).exists():
                raise serializers.ValidationError("You have already reported this comment.")
        return attrs


class UserBlockSerializer(serializers.ModelSerializer):
    """Serializer for blocking a user"""
    blocked_user_name = serializers.CharField(source='blocked.full_name', read_only=True)
    blocked_user_email = serializers.CharField(source='blocked.email', read_only=True)

    class Meta:
        model = UserBlock
        fields = ['id', 'blocked', 'blocked_user_name', 'blocked_user_email', 'reason', 'created_at']
        read_only_fields = ['id', 'blocked_user_name', 'blocked_user_email', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        blocked = attrs.get('blocked')
        if request and blocked:
            if blocked == request.user:
                raise serializers.ValidationError("You cannot block yourself.")
            if UserBlock.objects.filter(blocker=request.user, blocked=blocked).exists():
                raise serializers.ValidationError("You have already blocked this user.")
        return attrs


class BlockedUserListSerializer(serializers.ModelSerializer):
    """Serializer for listing blocked users"""
    blocked_user_id = serializers.UUIDField(source='blocked.id', read_only=True)
    blocked_user_name = serializers.CharField(source='blocked.full_name', read_only=True)
    blocked_user_email = serializers.CharField(source='blocked.email', read_only=True)
    blocked_user_avatar = serializers.ImageField(source='blocked.avatar', read_only=True)

    class Meta:
        model = UserBlock
        fields = ['id', 'blocked_user_id', 'blocked_user_name', 'blocked_user_email', 'blocked_user_avatar', 'reason', 'created_at']
        read_only_fields = ['id', 'blocked_user_id', 'blocked_user_name', 'blocked_user_email', 'blocked_user_avatar', 'reason', 'created_at']