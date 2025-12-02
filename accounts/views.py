import random
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from drf_spectacular.utils import extend_schema, inline_serializer
from accounts.serializers import (
    CustomTokenObtainPairSerializer, 
    ResetPasswordConfirmSerializer,
    RegisterSerializer,
    SubscriptionPlanSerializer, 
    UserSerializer, 
    VerifyEmailSerializer,
    CoachSerializer,
    ChangePasswordSerializer
)
from articles.models import Article
from workouts.models import UserWorkout
from workouts.serializers import UserWorkoutListSerializer
from articles.serializers import ArticleSerializer
from .models import User, OTP, Coach, SubscriptionPlan
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
            
            try:
                send_mail(
                    'Verify your email',
                    f'Your OTP for email verification is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                return Response({"message": "Otp sent successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Log the error for debugging
                print(f"Email sending failed: {str(e)}")
                # Still return success but with different message
                return Response({
                    "message": "Account created successfully. Email service temporarily unavailable.",
                    "otp": otp if settings.DEBUG else None  # Only show OTP in debug mode
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        try:
            email= request.data.get('email')
            input_otp = request.data.get('otp')
            
            if not email or not input_otp:
                return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user= User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
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
        except Exception as e:
            return Response({
                "error": "Failed to verify email.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class PasswordResetView(GenericAPIView):
#     serializer_class = PasswordResetSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             old_password = serializer.validated_data.get('old_password')

#         user = User.objects.filter(email=serializer.validated_data.get('email')).first()
#         if not user:
#             return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
#         if not user.check_password(old_password):
#             return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

#         otp = str(random.randint(1000, 9999))
#         OTP.objects.create(
#             user=user,
#             code=otp,
#             purpose='password_reset',
#             expires_at=timezone.now() + timezone.timedelta(minutes=10)
#         )
#         print(f"Sending OTP {otp} to email {user.email}")
#         send_mail(
#             'Password Reset OTP',
#             f'Your OTP for password reset is: {otp}',
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#         )


#         return Response({"message": "Otp sent successfully"}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):
        try:
            email= request.data.get('email')
            input_otp = request.data.get('otp')
            new_password = request.data.get('new_password')
            
            if not email or not input_otp or not new_password:
                return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user= User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
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
        except Exception as e:
            return Response({
                "error": "Failed to reset password.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class SendOTPView(GenericAPIView):
    @extend_schema(
        request=inline_serializer(
            name='SendOTPRequest',
            fields={
                'email': serializers.EmailField(),
                'purpose': serializers.CharField()
            }
        ),
        responses={
            200: inline_serializer(
                name='SendOTPResponse',
                fields={
                    'message': serializers.CharField()
                }
            )
        }
    )
    def post(self, request):
        email = request.data.get('email')
        purpose = request.data.get('purpose')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(1000, 9999))
        OTP.objects.create(
            user=user,
            code=otp,
            purpose=purpose,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        print(f"Sending OTP {otp} to email {user.email} for purpose {purpose}")
        
        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP for {purpose} is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            return Response({"message": "Otp sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error for debugging
            print(f"Email sending failed: {str(e)}")
            # Still return success but with different message
            return Response({
                "message": "OTP created successfully. Email service temporarily unavailable.",
                "otp": otp if settings.DEBUG else None  # Only show OTP in debug mode
            }, status=status.HTTP_200_OK)

class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(serializer.validated_data.get('old_password')):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=inline_serializer(
            name='LogoutRequest',
            fields={
                'refresh_token': serializers.CharField()
            }
        ),
        responses={
            205: inline_serializer(
                name='LogoutResponse',
                fields={
                    'message': serializers.CharField()
                }
            )
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class HomeAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='HomeAPIResponse',
                fields={
                    'workouts': UserWorkoutListSerializer(many=True).child,
                    'articles': ArticleSerializer(many=True).child
                }
            )
        }
    )
    def get(self, request):
        workouts = UserWorkout.objects.filter(user=request.user)
        articles = Article.objects.all()
        return Response(
            {
                "workouts": UserWorkoutListSerializer(workouts, many=True).data,
                "articles": ArticleSerializer(articles, many=True).data

            },
            status=status.HTTP_200_OK
        )

class SubscriptionPlanListView(GenericAPIView):
    permission_classes = []
    serializer_class = SubscriptionPlanSerializer
    
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        serializer = self.serializer_class(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)