#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission


class LuffyPermission(BasePermission):
    def __init__(self):
        self.message = "用户验证失败"

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user:
            return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True
