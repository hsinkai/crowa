# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.

import datetime
import time

from dateutil import tz
from django.contrib.auth import mixins, get_user
from rest_framework import serializers
from rest_framework import views, response, authentication, exceptions, generics
from rest_framework_jwt.settings import api_settings

from qiange.authentications import AccountAndPasswordAuthentication


class _TokenAuthorizationMixin(object):
    def generate_token(self, request):
        user = request.user
        payload = {
            # 'id': user.id,
            'username': user.username,
            'exp': time.mktime((datetime.datetime.now() + api_settings.JWT_EXPIRATION_DELTA).timetuple()),
        }
        return api_settings.JWT_ENCODE_HANDLER(payload)

    def authorize(self, request):
        now = datetime.datetime.now(tz=tz.gettz('Asia/Taipei'))
        expired_time = now + api_settings.JWT_EXPIRATION_DELTA
        payload = {
            'token': self.generate_token(request),
            'expired_time': expired_time,
        }
        return response.Response(payload)


class _AuthenticationMixin(object):
    def authenticate(self, request):
        for auth in self.get_authenticators():
            if auth.authenticate(request):
                break
        else:
            raise exceptions.AuthenticationFailed()


class JWTokenLoginRequiredAuthorizationView(mixins.LoginRequiredMixin, _TokenAuthorizationMixin, views.APIView, ):
    """
    取得 token：須登入。
    適合透過瀏覽器使用。
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        request.user = get_user(request)
        return self.authorize(request)


class TokenAuthorizationView(_AuthenticationMixin, _TokenAuthorizationMixin, generics.CreateAPIView):
    """
    取得 token：不需登入。
    未登入的用戶須提交username/password作為驗證憑據，適合程式調用。
    """
    authentication_classes = (AccountAndPasswordAuthentication, authentication.SessionAuthentication)
    permission_classes = ()

    class CredentialSerializer(serializers.Serializer):
        username = serializers.CharField(required=True, write_only=True, )
        password = serializers.CharField(required=True, write_only=True, )

        def create(self, validated_data, *args, **kwargs): pass
        def save(self, instance, validated_data, *args, **kwargs): pass

    serializer_class = CredentialSerializer

    def create(self, request, *args, **kwargs):
        self.authenticate(request)
        token_response = self.authorize(request)
        return token_response
