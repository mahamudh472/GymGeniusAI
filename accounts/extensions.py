from drf_spectacular.extensions import OpenApiAuthenticationExtension
from accounts.authentication import UpdateLastLoginJWT

class UpdateLastLoginJWTScheme(OpenApiAuthenticationExtension):
    target_class = 'accounts.authentication.UpdateLastLoginJWT'
    name = 'UpdateLastLoginJWT'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }