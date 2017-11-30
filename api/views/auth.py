#!/usr/bin/env python
# -*- coding:utf-8 -*-

from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models

from api.serializer.auth import AuthSerializer


class AuthView(APIView):
    """
    用户认证，认证成功后返回Token
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        response = {'code': 1000, 'errors': None}
        ser = AuthSerializer(data=request.data)
        if ser.is_valid():
            try:
                user = models.Account.objects.get(**ser.validated_data)
                token_obj, is_create = models.UserAuthToken.objects.update_or_create(user=user)
                response['token'] = token_obj.token
                response['name'] = user.username
                response['code'] = 1002
            except Exception as e:
                print(e)
                response['errors'] = '用户名密码验证异常'
                response['code'] = 1001
        else:
            response['errors'] = ser.errors

        return Response(response)
