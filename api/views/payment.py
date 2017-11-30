#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import datetime
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

from api.utils.auth.token_auth import LuffyTokenAuthentication
from api.utils.auth.token_permission import LuffyPermission
from api.utils import redis_pool
from repository import models


class PaymentView(APIView):
    """
    去结算接口
    """
    authentication_classes = [LuffyTokenAuthentication, ]
    permission_classes = [LuffyPermission, ]

    def get(self, request, *args, **kwargs):
        """
        获取结算列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1000}
        try:
            # 结算商品列表
            payment_list = redis_pool.conn.hget(settings.REDIS_PAYMENT_KEY, request.user.id)
            if not payment_list:
                raise Exception()

            response['data'] = {
                'payment_list': json.loads(payment_list.decode('utf-8')),  # 结算信息（课程、价格和优惠券）
                "balance": request.user.balance  # 个人贝里账户，可使用贝里金额
            }
        except Exception as e:
            response['code'] = 1001
            response['msg'] = "结算列表为空"

        return Response(response)

    def post(self, request, *args, **kwargs):
        """
        去结算
            方案一：用户提交课程id，去redis购物车中获取其选好的价格策略，再次检测课程和价格策略的合法性。
                   PS: 直接购买时，需要先加入购物车，再立即去结算
            方案二：用户提交课程id和价格策略id，去数据库验证其合法性。
                   PS: 直接购买时，直接去结算
            
            user.id: {
                policy_course_dict:{
                    课程ID:{
                        'course_id': course_id,
                        'course_name': product['name'],
                        'course_img': product['course_img'],
                        'policy_id': product['choice_policy_id'],
                        'policy_price': policy_price,
                        'policy_': policy_period,
                        'coupon_record_list': [
                            {'id': 0, 'text': '请选择优惠券'},
                            {'id': 1, 'type':1, 'text': '优惠券1', ..},
                            {'id': 2, 'type':2, 'text': '优惠券1', ..},
                            {'id': 3, 'type':3, 'text': '优惠券1', ..},
                        ],
                    },
                    课程ID:{
                        'course_id': course_id,
                        'course_name': product['name'],
                        'course_img': product['course_img'],
                        'policy_id': product['choice_policy_id'],
                        'policy_price': policy_price,
                        'policy_': policy_period,
                        'coupon_record_list': [
                            {'id': 0, 'text': '请选择优惠券'},
                            {'id': 1, 'type':1, 'text': '优惠券1', ..},
                            {'id': 2, 'type':2, 'text': '优惠券1', ..},
                            {'id': 3, 'type':3, 'text': '优惠券1', ..},
                        ],
                    }
                },
                global_coupon_dict:{
                    1:{'type': 0, 'text': "通用优惠券", 'id': 1, ..},
                    2:{'type': 0, 'text': "通用优惠券", 'id': 2, ..},
                    3:{'type': 0, 'text': "通用优惠券", 'id': 3, ...},
                    4:{'type': 0, 'text': "通用优惠券", 'id': 4, ...},
                }
            }  
                   
            
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1001}
        try:
            # 获取用户提交的课程id
            course_id_list = request.data.get('course_list')
            if not course_id_list or not isinstance(course_id_list, list):
                raise Exception('请选择要结算的课程')

            # 购物车中检查是否已经有课程（应该有课程的）
            product_dict = redis_pool.conn.hget(settings.REDIS_SHOPPING_CAR_KEY, request.user.id)
            if not product_dict:
                raise Exception('购物车无课程')

            # 购物车中是否有用户要购买的课程
            product_dict = json.loads(product_dict.decode('utf-8'))

            # ###### 课程、价格和优惠券 #######
            policy_course_dict = {}

            for course_id in course_id_list:
                course_id = str(course_id)
                product = product_dict.get(course_id)
                if not product:
                    raise Exception('购买的课程必须先加入购物车')

                policy_exist = False
                for policy in product['price_policy_list']:
                    if policy['id'] == product['choice_policy_id']:
                        policy_price = policy['price']
                        policy_period = policy['period']
                        policy_valid_period = policy['valid_period']
                        policy_exist = True
                        break
                if not policy_exist:
                    raise Exception('购物车中的课程无此价格')

                policy_course = {
                    'course_id': course_id,
                    'course_name': product['name'],
                    'course_img': product['course_img'],
                    'policy_id': product['choice_policy_id'],
                    'policy_price': policy_price,
                    'policy_period': policy_period,
                    'policy_valid_period': policy_valid_period,
                    'coupon_record_list': [
                        {'id': 0, 'text': '请选择优惠券'},
                    ],
                }
                policy_course_dict[course_id] = policy_course

            # 获取当前所有优惠券

            user_coupon_list = models.CouponRecord.objects.filter(account=request.user,
                                                                  status=0)
            # ###### 全局优惠券 #######
            global_coupon_record_dict = {}

            # 课程优惠券添加到课程中；全局优惠券添加到全局
            current_date = datetime.datetime.now().date()
            for record in user_coupon_list:
                # 检查优惠券是否已经过期
                begin_date = record.coupon.valid_begin_date
                end_date = record.coupon.valid_end_date
                if begin_date:
                    if current_date < begin_date:
                        continue
                if end_date:
                    if current_date > end_date:
                        continue
                # 全局优惠券
                if not record.coupon.content_type:
                    if record.coupon.coupon_type == 0:
                        temp = {'type': 0, 'text': "通用优惠券", 'id': record.id,
                                'begin_date': begin_date, 'end_date': end_date,
                                'money_equivalent_value': record.coupon.money_equivalent_value}
                    elif record.coupon.coupon_type == 1:
                        temp = {'type': 1, 'text': "满减券", 'id': record.id,
                                'begin_date': begin_date, 'end_date': end_date,
                                'minimum_consume': record.coupon.minimum_consume,
                                'money_equivalent_value': record.coupon.money_equivalent_value}
                    elif record.coupon.coupon_type == 2:
                        temp = {'type': 2, 'text': "折扣券", 'id': record.id,
                                'begin_date': begin_date, 'end_date': end_date,
                                'off_percent': record.coupon.off_percent}
                    else:
                        continue

                    global_coupon_record_dict[record.id] = temp
                # 课程优惠券
                else:
                    cid = record.coupon.object_id
                    if record.coupon.content_type.model == 'course' and cid in policy_course_dict:
                        # 课程价格：满减，打折，通用
                        if record.coupon.coupon_type == 0:
                            temp = {'type': 0, 'text': "通用优惠券", 'id': record.id,
                                    'begin_date': begin_date, 'end_date': end_date,
                                    'money_equivalent_value': record.coupon.money_equivalent_value}
                        elif record.coupon.coupon_type == 1 and policy_course_dict[cid][
                            'policy_price'] >= record.coupon.money_equivalent_value:
                            temp = {'type': 1, 'text': "满减券", 'id': record.id,
                                    'begin_date': begin_date, 'end_date': end_date,
                                    'minimum_consume': record.coupon.minimum_consume,
                                    'money_equivalent_value': record.coupon.money_equivalent_value}
                        elif record.coupon.coupon_type == 2:
                            temp = {'type': 2, 'text': "折扣券", 'id': record.id,
                                    'begin_date': begin_date, 'end_date': end_date,
                                    'off_percent': record.coupon.off_percent}
                        else:
                            continue
                        policy_course_dict[cid]['coupon_record_list'].append(temp)

            user_pay = {
                'policy_course_dict': policy_course_dict,
                'global_coupon_record_dict': global_coupon_record_dict
            }
            redis_pool.conn.hset(settings.REDIS_PAYMENT_KEY, request.user.id, json.dumps(user_pay))

        except Exception as e:
            response['code'] = 1002
            response['msg'] = str(e)

        return Response(response)
