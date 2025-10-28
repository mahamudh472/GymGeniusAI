from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import serializers
from .models import Notification
from .serializers import NotificationSerializer
from django_filters.rest_framework import DjangoFilterBackend

class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
        
class NotificationDetailView(CreateAPIView):
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