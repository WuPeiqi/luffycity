#!/usr/bin/env python
# -*- coding:utf-8 -*-
from repository import models
from rest_framework import serializers
from repository import models


class ShoppingCarSerializer(serializers.ModelSerializer):
    price_policy_list = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'course_img', 'price_policy_list']

    def get_price_policy_list(self, obj):
        ret = []
        for item in obj.price_policy.all():
            ret.append({'id': item.id, 'period': item.get_valid_period_display(),'valid_period': item.valid_period, 'price': item.price})
        return ret


class PaymentSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    coupons = serializers.SerializerMethodField()

    class Meta:
        model = models.PricePolicy
        fields = ['id', 'valid_period', 'price', 'course', 'coupons']

    def get_course(self, obj):
        ret = {
            'id': obj.content_object.id,
            'name': obj.content_object.name,
            'course_img': obj.content_object.course_img,
        }
        return ret

    def get_coupons(self, obj):
        ret = [
            {"id": 0, "text": "课程优惠券"}
        ]
        coupons = obj.content_object.coupon.all()
        for item in coupons:
            ret.append({'id': item.id, 'text': item.name})
        return ret
