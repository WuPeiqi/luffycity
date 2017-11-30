#!/usr/bin/env python
# -*- coding:utf-8 -*-

from repository import models
from rest_framework import serializers


class CourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = "__all__"


class MyListField(serializers.ListField):
    def __init__(self, fields=None, filter_kwargs=None, *args, **kwargs):
        super(MyListField, self).__init__(*args, **kwargs)
        self.fields = fields
        self.filter_kwargs = filter_kwargs if filter_kwargs else {}

    def get_attribute(self, instance):
        return instance.recommend_courses.filter(**self.filter_kwargs)

    def to_representation(self, value):

        if not self.fields:
            from django.utils import six
            return six.text_type(value)

        result = []
        for row in value:
            temp = {}
            for field in self.fields:
                temp[field] = getattr(row, field)
            result.append(temp)
        return result


class CourseDetailModelSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name')
    # recommends = serializers.ListField(child=serializers.CharField(), source='recommend_courses.all')
    recommends = MyListField(fields=['id', 'name'], child=serializers.CharField())

    # x = serializers.SerializerMethodField()

    class Meta:
        model = models.CourseDetail
        fields = ['id', 'hours', 'course_slogan', 'video_brief_link', 'why_study', 'what_to_study_brief',
                  'career_improvement', 'prerequisite', 'course_name', 'recommends', ]
        depth = 1


class PricePolicyModelSerializer(serializers.ModelSerializer):
    period = serializers.CharField(source='get_valid_period_display')

    class Meta:
        model = models.PricePolicy
        fields = ['id', 'valid_period', 'price', 'period']
