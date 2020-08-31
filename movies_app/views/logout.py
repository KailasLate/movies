from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import GenericAPIView
from utility.utils import revoke_oauth_token
from ..serializers.login_serializer import LoginSerializer
from utility.response import ApiResponse
from movies_app.models import User

class LogoutView(GenericAPIView, ApiResponse):
    serializer_class = LoginSerializer
    authentication_classes = [OAuth2Authentication]

    def get(self, request, *args, **kwargs):
        try:
            # capture data
            response = revoke_oauth_token(request)
            return ApiResponse.response_ok(self, message='Logout successful', data=response)
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])