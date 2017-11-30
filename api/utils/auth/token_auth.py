#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header
from django.utils.translation import ugettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, exceptions


class LuffyTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """

        # HTTP_AUTHORIZATION 请求头中对应的值应该为：Token QWxhZGRpbjpvcGVuIHNlc2FtZQ==
        # Token QWxhZGRpbjpvcGVuIHNlc2FtZQ==
        # auth = get_authorization_header(request).split()
        # if not auth or auth[0].lower() != self.keyword.lower().encode():
        #     # 未获取到授权请求头
        #     return None
        #
        # # 授权请求头值太短
        # if len(auth) == 1:
        #     msg = _('Invalid token header. No credentials provided.')
        #     raise exceptions.AuthenticationFailed(msg)
        #
        # # 授权请求头值太长
        # elif len(auth) > 2:
        #     msg = _('Invalid token header. Token string should not contain spaces.')
        #     raise exceptions.AuthenticationFailed(msg)
        #
        # try:
        #     token = auth[1].decode()
        # except UnicodeError:
        #     # 授权请求头值格式错误
        #     msg = _('Invalid token header. Token string should not contain invalid characters.')
        #     raise exceptions.AuthenticationFailed(msg)
        from rest_framework.request import Request
        token = request.query_params.get('token')
        if not token:
            raise exceptions.AuthenticationFailed('验证失败')

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        from repository.models import UserAuthToken
        try:
            token_obj = UserAuthToken.objects.select_related('user').get(token=token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return (token_obj.user, token_obj)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return self.keyword
