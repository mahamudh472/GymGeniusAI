from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import UserSerializer
from .models import User, OTP
from rest_framework.generics import RetrieveAPIView
from django.core.mail import send_mail
from django.utils import timezone
import random

class LoginView(APIView):
    def post(self, request):
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    
class VerifyEmailView(APIView):
    def post(self, request):
        event = request.session.get('event', None)
        if not event:
            return Response({"error": "Invalid otp"}, status=status.HTTP_400_BAD_REQUEST)
        email= request.data.get('email')
        input_otp = request.data.get('otp')

        if OTP.objects.filter(user__email=email, code=input_otp, purpose=event).exists():
            otp_record = OTP.objects.get(user__email=email, code=input_otp, purpose=event)
            if otp_record.is_valid():
                request.user.set_password(request.session.get('new_password'))
                request.user.save()
                otp_record.is_used = True
                otp_record.save()
                return Response({"message": f"Password successfully reset for {email}"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "OTP is expired or already used"}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))
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
            ['magentadyanne@tiffincrane.com'],
        )
        request.session['event'] = "password_reset"

        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
    

class ProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)