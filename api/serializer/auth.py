#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework import serializers
from rest_framework import fields


class PasswordValidator(object):
    def __init__(self, length):
        self.length = length

    def __call__(self, value):
        if len(value) < self.length:
            message = '密码长度太短了'
            raise serializers.ValidationError(message)

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # 执行验证之前调用,serializer_fields是当前字段对象
        pass


class AuthSerializer(serializers.Serializer):
    username = fields.CharField(error_messages={'required': '用户不能为空'})
    password = fields.CharField(error_messages={'required': '密码不能为空'}, validators=[PasswordValidator(3)])
