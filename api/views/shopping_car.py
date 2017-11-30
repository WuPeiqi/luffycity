#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response

from repository import models

from api.serializer.payment import ShoppingCarSerializer
from api.utils.auth.token_auth import LuffyTokenAuthentication
from api.utils.auth.token_permission import LuffyPermission
from api.utils import redis_pool
from api.utils.exception import PricePolicyDoesNotExist


class ShoppingCarView(ViewSetMixin, APIView):
    """
    购物车接口
    """
    authentication_classes = [LuffyTokenAuthentication, ]
    permission_classes = [LuffyPermission, ]

    def get(self, request, *args, **kwargs):
        """
        根据用户ID获取购物车所有东西
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1000, 'data': None}
        try:
            product_dict = redis_pool.conn.hget(settings.REDIS_SHOPPING_CAR_KEY, request.user.id)
            if product_dict:
                product_dict = json.loads(product_dict.decode('utf-8'))
                response['data'] = product_dict
        except Exception as e:
            response['code'] = 1001
            response['msg'] = "获取购物车列表失败"

        return Response(response)

    def post(self, request, *args, **kwargs):
        """
        # 根据课程ID获取课程信息以及相关所有价格策略
        chopping_car = {
            request.user.id:{
                course.id:{
                        title:'xx',
                        img:'xx',
                        choice_policy_id:1,
                        price_policy_list:[
                            {id:1,price:'9.9', period:'1个月'},
                            {id:2,price:'19.9',period:'3个月'},
                            {id:3,price:'59.9',period:'8个月'},
                        ],
                    }
                }，
                course.id:[
                        title:'xx',
                        img:'xx',
                        choice_policy_id:1,
                        price_policy_list:[
                            {id:1,price:'9.9', period:'1个月'},
                            {id:2,price:'19.9',period:'3个月'},
                            {id:3,price:'59.9',period:'8个月'},
                        ],
                    ]
                }
            }
        }
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """

        response = {'code': 1000, 'msg': None}
        try:
            course_id = int(request.data.get('course_id'))
            policy_id = int(request.data.get('policy_id'))

            # 获取课程信息
            course = models.Course.objects.exclude(course_type=2).filter(status=0).get(id=course_id)

            # 序列化课程信息，并获取其关联的所有价格策略
            ser = ShoppingCarSerializer(instance=course, many=False)
            product = ser.data

            # 判断价格策略是否存在
            policy_exist = False
            for policy in product['price_policy_list']:
                if policy['id'] == policy_id:
                    policy_exist = True
                    break
            if not policy_exist:
                raise PricePolicyDoesNotExist()

            # 设置默认选中的价格策略
            product.setdefault('choice_policy_id', policy_id)
            # 获取当前用户在购物车中已存在的课程，如果存在则更新，否则添加新课程
            product_dict = redis_pool.conn.hget(settings.REDIS_SHOPPING_CAR_KEY, request.user.id)
            if not product_dict:
                product_dict = {course_id: product}
            else:
                product_dict = json.loads(product_dict.decode('utf-8'))
                product_dict[course_id] = product
            # 将新课程写入到购物车
            redis_pool.conn.hset(settings.REDIS_SHOPPING_CAR_KEY, request.user.id, json.dumps(product_dict))

        except ObjectDoesNotExist as e:
            response['code'] = 1001
            response['msg'] = '视频不存在'
        except PricePolicyDoesNotExist as e:
            response['code'] = 1002
            response['msg'] = '价格策略不存在'
        except Exception as e:
            print(e)
            response['code'] = 1003
            response['msg'] = '添加购物车失败'

        return Response(response)

    def delete(self, request, *args, **kwargs):
        """
        删除购物车中的课程
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1000}
        try:
            course_id = kwargs.get('pk')
            product_dict = redis_pool.conn.hget(settings.REDIS_SHOPPING_CAR_KEY, request.user.id)
            if not product_dict:
                raise Exception('购物车中无课程')
            product_dict = json.loads(product_dict.decode('utf-8'))
            if course_id not in product_dict:
                raise Exception('购物车中无该商品')
            del product_dict[course_id]
            redis_pool.conn.hset(settings.REDIS_SHOPPING_CAR_KEY, request.user.id, json.dumps(product_dict))
        except Exception as e:
            response['code'] = 1001
            response['msg'] = str(e)

        return Response(response)

    def put(self, request, *args, **kwargs):
        """
        更新购物车中的课程的默认的价格策略
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1000}
        try:
            course_id = kwargs.get('pk')
            policy_id = request.data.get('policy_id')
            product_dict = redis_pool.conn.hget(settings.REDIS_SHOPPING_CAR_KEY, request.user.id)
            if not product_dict:
                raise Exception('购物车清单不存在')
            product_dict = json.loads(product_dict.decode('utf-8'))
            if course_id not in product_dict:
                raise Exception('购物车清单中商品不存在')

            policy_exist = False
            for policy in product_dict[course_id]['price_policy_list']:
                if policy['id'] == policy_id:
                    policy_exist = True
                    break
            if not policy_exist:
                raise PricePolicyDoesNotExist()

            product_dict[course_id]['choice_policy_id'] = policy_id
            redis_pool.conn.hset(settings.REDIS_SHOPPING_CAR_KEY, request.user.id, json.dumps(product_dict))
        except PricePolicyDoesNotExist as e:
            response['code'] = 1001
            response['msg'] = '价格策略不存在'
        except Exception as e:
            response['code'] = 1002
            response['msg'] = str(e)

        return Response(response)
