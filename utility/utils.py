import requests
from django.core.validators import validate_email
from django.core.paginator import Paginator
from django.conf import settings
from random import randint
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from oauthlib.oauth2.rfc6749.tokens import random_token_generator
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.settings import oauth2_settings
from datetime import datetime, timedelta
from movies_app.models import User
from utility.constants import *

""" mixins to handle request url """


class CreateRetrieveUpdateViewSet(GenericViewSet,
                                  mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin):
    pass


class MultipleFieldPKModelMixin(object):
    """
    Class to override the default behaviour for .get_object for models which have retrieval on fields
    other  than primary keys.
    """
    lookup_field = []
    lookup_url_kwarg = []

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        get_args = {field: self.kwargs[field] for field in
                    self.lookup_field if field in self.kwargs}

        get_args.update({'pk': self.kwargs[field] for field in
                         self.lookup_url_kwarg if field in self.kwargs})
        return get_object_or_404(queryset, **get_args)


""" email validations """


def is_valid_email(email):
    try:
        validate_email(email)
    except:
        return False
    return True

""" pagination response """
def get_pagination_resp(data, request):
    page_response = {"total_count": None, "total_pages": None,
                     "current_page": None, "limit": None}
    if request.query_params.get('type') == 'all':
        return {"data": data}

    page = request.query_params.get('page') if request.query_params.get('page') else 1
    limit = request.query_params.get('limit') if request.query_params.get('limit') else settings.PAGE_SIZE
    paginator = Paginator(data, limit)
    category_data = paginator.get_page(page).object_list
    page_response = {"total_count": paginator.count, "total_pages": paginator.num_pages,
                     "current_page": page, "limit": limit}
    current_page = paginator.num_pages
    paginator = {"paginator": page_response}
    if int(current_page) < int(page):
        return {"data": [], "paginator": paginator.get('paginator')}
        # return {"data": [], **paginator}
    response_data = {"data": category_data, "paginator": paginator.get('paginator')}
    return response_data

""" login token generations """
def generate_token(request, user):
    expire_seconds = oauth2_settings.user_settings['ACCESS_TOKEN_EXPIRE_SECONDS']
    scopes = oauth2_settings.user_settings['SCOPES']

    application = Application.objects.first()
    expires = datetime.now() + timedelta(seconds=expire_seconds)
    access_token = AccessToken.objects.create(
        user=user,
        application=application,
        token=random_token_generator(request),
        expires=expires,
        scope=scopes)

    refresh_token = RefreshToken.objects.create(
        user=user,
        token=random_token_generator(request),
        access_token=access_token,
        application=application)

    token = {
        'access_token': access_token.token,
        'token_type': 'Bearer',
        'expires_in': expire_seconds,
        'refresh_token': refresh_token.token,
        'scope': scopes}
    return token


def get_login_response(user=None, token=None):
    resp_dict = dict()
    resp_dict["id"] = user.id
    resp_dict["first_name"] = user.first_name
    resp_dict["last_name"] = user.last_name
    resp_dict["email"] = user.email
    resp_dict["role"] = user.role_id
    return resp_dict

""" token generations by oauth """


def generate_oauth_token(host, username, password):
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'grant_type': 'password',
               'username': username,
               'password': password,
               'client_id': client_id,
               'client_secret': client_secret}
    return (requests.post(settings.SERVER_PROTOCOLS + host + "/o/token/",
                          data=payload, headers=headers))

""" revoke token """
def revoke_oauth_token(request):
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'token': request.META['HTTP_AUTHORIZATION'][7:],
               'token_type_hint': 'access_token',
               'client_id': client_id,
               'client_secret': client_secret}

    # host request
    host = request.get_host()
    response = requests.post(settings.SERVER_PROTOCOLS + host + "/o/revoke_token/", data=payload,
                             headers=headers)
    return response



def get_serielizer_error(serializer):
    msg_list = []
    try:
        mydict = serializer.errors
        for key in sorted(mydict.keys()):
            msg = key + " : " + str(mydict.get(key)[0])
            msg_list.append(msg)
    except:
        msg_list = ["Invalid format"]
    return msg_list

def transform_list(self, data):
    return map(self.transform_single, data)

def is_admin_view(request):
    try:
        return request.user.role.id == 1
    except:
        return False


def is_user_view(request):
    try:
        return request.user.role.id == 2
    except:
        return False