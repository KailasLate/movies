from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group, User
from django.utils.translation import ugettext_lazy as _


class EmailOrUsernameModelBackend(object):

    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


""" Import all the models """
from .model.roles import Roles
from .model.users import User
from .model.movies import Movies