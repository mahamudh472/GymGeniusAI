from rest_framework import generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from .models import (
    ExerciseCategory, Exercise, UserWorkout, UserExercise, WorkoutProgress
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseSerializer, UserWorkoutListSerializer,
    UserWorkoutSerializer, UserExerciseSerializer, WorkoutProgressSerializer
)
from accounts.permissions import IsActiveUser

class UserWorkoutListAPIView(generics.ListAPIView):
    queryset = UserWorkout.objects.all()
    serializer_class = UserWorkoutListSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user).prefetch_related('user_exercises__exercise')
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.capitalize())
        return queryset

class UserWorkoutDetailAPIView(generics.RetrieveAPIView):
    queryset = UserWorkout.objects.all()
    serializer_class = UserWorkoutSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).prefetch_related('user_exercises__exercise')

from .utils import generate_workouts_for_user

@api_view(['GET', 'POST'])
@permission_classes([IsActiveUser])
def test(request):
    print(generate_workouts_for_user(user=request.user))
    return Response({"message": "Test successful"})