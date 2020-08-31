import json
import requests
from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView
from ..models import EmailOrUsernameModelBackend
from ..serializers.login_serializer import LoginSerializer
from ..model.users import User
from rest_framework.response import Response
from utility.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.conf import settings
from utility.utils import generate_token, get_login_response, generate_oauth_token
from utility.constants import STATUS_INACTIVE, STATUS_ACTIVE


class LoginViewSet(GenericAPIView, ApiResponse, EmailOrUsernameModelBackend):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            host = request.get_host()
            username = request.data.get('email')
            password = request.data.get('password')

            if not username or not password:
                return ApiResponse.response_bad_request(self, message='Mobile and Password are required')

            ''' authenticate user and generate token '''
            user = EmailOrUsernameModelBackend.authenticate(self, username=username, password=password)

            if user and user.status == STATUS_INACTIVE:
                return ApiResponse.response_bad_request(self, message='User is inactive please contact to admin')

            if user:
                '''
                Authorize to user
                '''
                # token = generate_token(request, user)
                token = generate_oauth_token(host, username, password)
                if token.status_code == 200:
                    resp_dict = get_login_response(user, token)
                    resp_dict['token'] = token.json()
                    Users.objects.filter(pk=user.id).update(current_status="online")
                    return ApiResponse.response_ok(self, data=resp_dict, message='Login successful')
                else:
                    return ApiResponse.response_bad_request(self, message='User Not Authorized')
            else:
                return ApiResponse.response_unauthorized(self,
                                                         message='Invalid username or password. Please try again.')
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args)])
