from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import WorkoutCategory, Workout, WorkoutRound, Exercise, UserWorkoutProgress
from .serializers import (
    WorkoutCategorySerializer, WorkoutSerializer,
    WorkoutRoundSerializer, ExerciseSerializer,
    UserWorkoutProgressSerializer
)
from accounts.permissions import IsActiveUser

class WorkoutCategoryListCreateView(ListCreateAPIView):
    queryset = WorkoutCategory.objects.all()
    serializer_class = WorkoutCategorySerializer
    permission_classes = [IsActiveUser]

class WorkoutCategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = WorkoutCategory.objects.all()
    serializer_class = WorkoutCategorySerializer
    permission_classes = [IsActiveUser]

class WorkoutListCreateView(ListCreateAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsActiveUser]

class WorkoutDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsActiveUser]

class WorkoutRoundListCreateView(ListCreateAPIView):
    queryset = WorkoutRound.objects.all()
    serializer_class = WorkoutRoundSerializer
    permission_classes = [IsActiveUser]

class WorkoutRoundDetailView(RetrieveUpdateDestroyAPIView):
    queryset = WorkoutRound.objects.all()
    serializer_class = WorkoutRoundSerializer
    permission_classes = [IsActiveUser]

class ExerciseListCreateView(ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsActiveUser]

class ExerciseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsActiveUser]

class UserWorkoutProgressListCreateView(ListCreateAPIView):
    queryset = UserWorkoutProgress.objects.all()
    serializer_class = UserWorkoutProgressSerializer
    permission_classes = [IsActiveUser]

class UserWorkoutProgressDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserWorkoutProgress.objects.all()
    serializer_class = UserWorkoutProgressSerializer
    permission_classes = [IsActiveUser]