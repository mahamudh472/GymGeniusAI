# favorites/views.py
from rest_framework import generics, permissions, views, filters, serializers
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from articles.serializers import ArticleSerializer
from .models import Favorite, FAQ, ContactOption, Notification, PrivacyPolicy
from nutrition.models import Meal
from .serializers import FavoriteSerializer, FAQSerializer, ContactOptionSerializer, NotificationSerializer
from workouts.serializers import UserWorkoutListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from articles.models import Article
from fcm_django.models import FCMDevice
from firebase_admin .messaging import Message, Notification as FCMNotification, UnregisteredError
# from nutrition.serializers import MealSerializer

def add_notification(user, title, message, notification_type):
    """Utility function to add a notification for a user."""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    devices = FCMDevice.objects.filter(user=user)
    for device in devices:
        try:
            response = device.send_message(
                Message(
                    notification=FCMNotification(
                        title=title,
                        body=message
                    )
                )
            )
            print(f"Success: device={device.id}, msg_id={response}")

        except UnregisteredError:
            print(f"❌ Device {device.id} is no longer registered. Removing...")
            device.delete()  # recommended

        except Exception as e:
            print(f"❌ Failed sending to device {device.id}: {e}")
        except Exception as e:
            print(f"Failed to send notification to device {device.id}: {e}")
 

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'created_at']

    def get_queryset(self):
        # Protect against unauthenticated requests during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)
        

class NotificationDetailView(generics.CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED
        )

class MarkAllNotificationsReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer  # Add serializer_class for schema generation

    @extend_schema(
        request=None,  # This endpoint doesn't require a request body
        responses={
            200: inline_serializer(
                name='MarkAllNotificationsReadResponse',
                fields={
                    'detail': serializers.CharField()
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        updated_count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response(
            {"detail": f"Marked {updated_count} notifications as read."},
            status=status.HTTP_200_OK
        )

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class FavoriteToggleView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            favorite = serializer.save()
            if not favorite.id:
                return Response(
                    {"detail": "Removed from favorites."},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Added to favorites."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Handle "Removed from favorites" message
            if isinstance(e, serializers.ValidationError) and 'Removed' in str(e):
                return Response({"detail": "Removed from favorites."}, status=status.HTTP_200_OK)
            raise e


class SearchResultsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserWorkoutListSerializer  # Add serializer_class for schema generation

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Search query'
            )
        ],
        responses={
            200: inline_serializer(
                name='SearchResultsResponse',
                fields={
                    'workouts': UserWorkoutListSerializer(many=True),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            query = request.query_params.get('q', '')
            user = request.user
            from django.db.models import Q
            from workouts.models import UserWorkout
            
            # Search user's workouts
            user_workouts = UserWorkout.objects.filter(
                Q(user=user)
                & (
                    Q(name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(difficulty__icontains=query)
                    | Q(user_exercises__exercise__name__icontains=query)
                    | Q(user_exercises__exercise__muscle_group__icontains=query)
                )
            ).distinct()
            
            meals = Meal.objects.filter(user=request.user, title__icontains=query)
            workout_serializer = UserWorkoutListSerializer(user_workouts, many=True)
            articles = Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).distinct()
            article_serializer = ArticleSerializer(articles, many=True)
            # meal_serializer = MealSerializer(meals, many=True)
            return Response({
                "workouts": workout_serializer.data,
                "articles": article_serializer.data,
                # "meals": meal_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Failed to search.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class FavoriteToggleView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            favorite = serializer.save()
            if not favorite.id:
                return Response(
                    {"detail": "Removed from favorites."},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Added to favorites."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Handle "Removed from favorites" message
            if isinstance(e, serializers.ValidationError) and 'Removed' in str(e):
                return Response({"detail": "Removed from favorites."}, status=status.HTTP_200_OK)
            raise e


class FAQListView(generics.ListAPIView):

    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['question', 'answer', 'type']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type']


class ContactOptionListView(generics.ListAPIView):

    queryset = ContactOption.objects.all()
    serializer_class = ContactOptionSerializer
    permission_classes = [permissions.AllowAny]

class PrivacyPolicyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='PrivacyPolicyResponse',
                fields={
                    'content': serializers.CharField(),
                    'updated_at': serializers.DateTimeField()
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            policy = PrivacyPolicy.objects.latest('updated_at')
            return Response(
                {
                    "content": policy.content,
                    "updated_at": policy.updated_at
                },
                status=status.HTTP_200_OK
            )
        except PrivacyPolicy.DoesNotExist:
            return Response(
                {"detail": "Privacy policy not found."},
                status=status.HTTP_404_NOT_FOUND
            )


from rest_framework.decorators import (
    api_view, permission_classes
) 
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from fcm_django.models import FCMDevice
 
class DeviceTokenRegisterRequest(serializers.Serializer):
    device_token = serializers.CharField()
 
 
@extend_schema(request=DeviceTokenRegisterRequest)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device_token(request):
    device_token = request.data.get('device_token')
    if not device_token:
        print("invalid token",device_token, device_token=="")
        raise ValidationError({
            "error": "'device_token' is required"
        })

    print("LOGGING ", device_token)

    FCMDevice.objects.update_or_create(
        user=request.user,
        defaults={
            'registration_id': device_token,
        }
    )
    return Response({
        "success": True
    })
 
 
# @extend_schema(request=DeviceTokenRegisterRequest)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_device_token(request):
    FCMDevice.objects.filter(user=request.user).delete()
    return Response({
        "success": True
    })

 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_demo_notification(request):
    from utils.views import add_notification
    add_notification(
        user=request.user,
        title="Demo Notification",
        message="This is a demo notification.",
        notification_type="info"
    )
    return Response({
        "success": True
    })