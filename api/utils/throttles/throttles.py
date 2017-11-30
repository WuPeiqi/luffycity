#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.throttling import SimpleRateThrottle


class LuffyAnonRateThrottle(SimpleRateThrottle):
    """
    匿名用户，根据IP进行限制
    """
    scope = "luffy_anon"

    def get_cache_key(self, request, view):
        if request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

    def allow_request(self, request, view):
        # self.duration      N秒
        # self.num_requests  允许请求次数

        self.key = self.get_cache_key(request, view)
        # 用户已经登录，不再通过匿名限制
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def throttle_success(self):
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    def throttle_failure(self):
        """
        Called when a request to the API has failed due to throttling.
        """
        return False


class LuffyUserRateThrottle(SimpleRateThrottle):
    """
    登录用户，根据用户token限制
    """
    scope = "luffy_user"

    def get_ident(self, request):
        """
        认证成功时：request.user是用户对象；request.auth是token对象
        :param request: 
        :return: 
        """
        return request.auth.token

    def get_cache_key(self, request, view):
        """
        获取缓存key
        :param request: 
        :param view: 
        :return: 
        """
        # 未登录用户，无需进行用户节流限制
        if not request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class LuffyMessageRateThrottle(SimpleRateThrottle):
    """
    发送短信的节流规则
    """
    scope_attr = 'luffy_msg_scope'

    scope = "luffy_msg"

    luffy_throttle_request_key = 'phone'

    def get_cache_key(self, request, view):
        """
        获取缓存key
        :param request: 
        :param view: 
        :return: 
        """
        # 获取用户手机号，未输入手机号则无需验证
        phone = request.data.get(self.luffy_throttle_request_key)
        if not phone:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': phone
        }
