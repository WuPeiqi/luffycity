#!/usr/bin/env python
# -*- coding:utf-8 -*-
from .base import MiddlewareMixin


class CorsMiddleware(MiddlewareMixin):

    def process_response(self,request,response):
        response['Access-Control-Allow-Origin'] = "*"
        response['Access-Control-Allow-Headers'] = "Content-Type"
        return response

