#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models
from rest_framework import serializers
from api.serializer.course import CourseModelSerializer
from api.serializer.course import CourseDetailModelSerializer
from api.serializer.course import PricePolicyModelSerializer


class CourseView(APIView):
    def get(self, request, *args, **kwargs):
        response = {'status': False}
        try:
            pk = kwargs.get('pk')
            if not pk:
                queryset = models.Course.objects.exclude(course_type=2).order_by('order')[0:3]
                ser = CourseModelSerializer(instance=queryset, many=True)
            else:
                queryset = models.CourseDetail.objects.get(course_id=pk)
                ser = CourseDetailModelSerializer(instance=queryset, many=False)
            response['data'] = ser.data
            response['status'] = True
        except Exception as e:
            response['error'] = str(e)
        return Response(response)


class PricePolicyView(APIView):
    def get(self, request, *args, **kwargs):
        response = {'status': False}
        try:
            course_id = kwargs.get('course_id')
            course_obj = models.Course.objects.get(pk=course_id)
            queryset = course_obj.price_policy.all()
            ser = PricePolicyModelSerializer(instance=queryset, many=True)
            response['data'] = ser.data
            response['status'] = True
        except Exception as e:
            response['error'] = str(e)
        return Response(response)



