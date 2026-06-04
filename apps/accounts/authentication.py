from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import timedelta

class UpdateLastLoginJWT(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, validated_token = result
            now = timezone.now()
            if user.last_login is None or user.last_login <= now - timedelta(minutes=5):
                user.last_login = now
                user.save(update_fields=["last_login"])
        return result
