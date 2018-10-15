# -*- coding: utf-8 -*-

import jwt
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.utils import jwt_decode_handler

from qiange.util import extract_incoming

USERNAME = 'username'
PASSWORD = 'password'


def get_token(request, token_name):
    try:
        token = request.META.get('HTTP_AUTHORIZATION') or request.query_params.get(token_name) or b''
    except Exception:
        raise AuthenticationFailed()
    else:
        if token and 'BASIC' not in token.upper():
            return token.split('JWT ')[-1]


class AccountAndPasswordAuthentication(BaseAuthentication):
    def authenticate(self, request):
        incoming = extract_incoming(request)
        if not isinstance(incoming, dict):
            raise AuthenticationFailed()
        username, password = incoming.get(USERNAME), incoming.get(PASSWORD)
        if not username or not password:
            return None
        user = ModelBackend().authenticate(request, username, password)
        if user is None:
            raise AuthenticationFailed('%s or %s is incorrect.' % (USERNAME, PASSWORD))
        if not user.is_active:
            raise AuthenticationFailed("Invalid Login.")
        return user, None

    def authenticate_header(self, request):
        return '%s:%s' % (USERNAME, PASSWORD)


class JWTokenAuthentication(BaseAuthentication):
    token_name = 'token'

    def authenticate(self, request):
        token = get_token(request, self.token_name)
        if not token:
            return None
        try:
            payload = jwt_decode_handler(token)
            # user_id = payload.get('id')
            username = payload.get('username')
            user = User.objects.get(username=username)
        except jwt.ExpiredSignature:
            raise AuthenticationFailed("Expired %s." % self.token_name)
        except (jwt.DecodeError, Exception):
            raise AuthenticationFailed("Corrupted %s." % self.token_name)
        return user, None

    def authenticate_header(self, request):
        return self.token_name
