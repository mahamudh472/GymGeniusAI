# favorites/views.py
from rest_framework import generics, permissions, views, filters
from rest_framework.response import Response
from rest_framework import status
from .models import Favorite, FAQ, ContactOption
from nutrition.models import Meal
from .serializers import FavoriteSerializer, FAQSerializer, ContactOptionSerializer
from rest_framework import serializers
from workouts.serializers import UserWorkoutListSerializer
from django_filters.rest_framework import DjangoFilterBackend
# from nutrition.serializers import MealSerializer

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


class SearchResultsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
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
        # meal_serializer = MealSerializer(meals, many=True)
        return Response({
            "workouts": workout_serializer.data,
            # "meals": meal_serializer.data
        }, status=status.HTTP_200_OK)

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
