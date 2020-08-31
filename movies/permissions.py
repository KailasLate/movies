from rest_framework.permissions import BasePermission
from django.conf import settings
from django.core.exceptions import PermissionDenied
from utility.response import ApiResponse

class is_access(BasePermission):
    def has_permission(self, request, view):
        headers = settings.HEADERS
        return request.META.get('HTTP_ACCESS_KEY') == headers

def is_login(f):
    def validate(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return ApiResponse.response_unauthenticate(self)
        return f(self, request, *args, **kwargs)

    return validate