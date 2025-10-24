import random
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from accounts.serializers import (
    CustomTokenObtainPairSerializer, 
    PasswordResetSerializer, 
    RegisterSerializer, 
    ResetPasswordConfirmSerializer, 
    UserSerializer, 
    VerifyEmailSerializer,
    CoachSerializer
)
from .models import User, OTP, Coach
from .permissions import IsActiveUser

class LoginView(APIView):
    def post(self, request):
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_verified=False)
            otp = str(random.randint(1000, 9999))
            OTP.objects.create(
                user=user,
                code=otp,
                purpose='signup',
                expires_at=timezone.now() + timezone.timedelta(minutes=10)
            )
            print(f"Sending OTP {otp} to email {user.email}")
            send_mail(
                'Verify your email',
                f'Your OTP for email verification is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            return Response({"message": "Otp sent successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        email= request.data.get('email')
        input_otp = request.data.get('otp')
        user= User.objects.filter(email=email).first()
        purpose= "signup"

        if OTP.objects.filter(user__email=email, code=input_otp, purpose=purpose).exists():
            otp_record = OTP.objects.get(user__email=email, code=input_otp, purpose=purpose)
            if otp_record.is_valid():
                user = otp_record.user
                user.is_verified = True
                user.save()
                otp_record.is_used = True
                otp_record.save()
                return Response({"message": f"Email {email} successfully verified"}, status=status.HTTP_200_OK)
                
            else:
                return Response({"error": "OTP is expired or already used"}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')

        user = User.objects.filter(email=serializer.validated_data.get('email')).first()
        if not user:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(1000, 9999))
        OTP.objects.create(
            user=user,
            code=otp,
            purpose='password_reset',
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        print(f"Sending OTP {otp} to email {user.email}")
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )


        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):

        email= request.data.get('email')
        input_otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        user= User.objects.filter(email=email).first()
        purpose= "password_reset"

        if OTP.objects.filter(user__email=email, code=input_otp, purpose=purpose).exists():
            otp_record = OTP.objects.get(user__email=email, code=input_otp, purpose=purpose)
            if otp_record.is_valid():
                user = otp_record.user
                user.set_password(new_password)
                user.save()
                otp_record.is_used = True
                otp_record.save()
                return Response({"message": f"Password successfully reset for {email}"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "OTP is expired or already used"}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProfileView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CoachListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoachSerializer
    
    def get(self, request):
        coaches = Coach.objects.all()
        serializer = self.serializer_class(coaches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)