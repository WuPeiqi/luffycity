#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from api.utils.alipay import AliPay
from repository import models


class AlipayView(APIView):
    def get(self, request, *args, **kwargs):
        """
        支付成功后，支付宝回调的return地址
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        params = request.GET.dict()
        sign = params.pop('sign', None)
        pay = AliPay(debug=True)
        status = pay.verify(params, sign)
        if status:
            return Response('支付成功')
        else:
            return Response('支付失败')

    def post(self, request, *args, **kwargs):
        """
        支付成功后，支付宝回调的notify地址
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        try:
            response = {'code': 1002}
            from urllib.parse import parse_qs

            # request.body                  => 字节类型
            # request.body.decode('utf-8')  => 字符串类型
            """
            {"k1":["v1"],"k2":["v1"]}
            k1=[v1]&k2=[v2]
            """
            body_str = request._request.body.decode('utf-8')
            post_data = parse_qs(body_str)
            # {k1:[v1,],k2:[v2,]}

            # {k1:v1}
            post_dict = {}
            for k, v in post_data.items():
                post_dict[k] = v[0]

            print(post_dict)
            """
            {'gmt_create': '2017-11-24 14:53:41', 'charset': 'utf-8', 'gmt_payment': '2017-11-24 14:53:48', 'notify_time': '2017-11-24 14:57:05', 'subject': '充气式韩红', 'sign': 'YwkPI9BObXZyhq4LM8//MixPdsVDcZu4BGPjB0qnq2zQj0SutGVU0guneuONfBoTsj4XUMRlQsPTHvETerjvrudGdsFoA9ZxIp/FsZDNgqn9i20IPaNTXOtQGhy5QUetMO11Lo10lnK15VYhraHkQTohho2R4q2U6xR/N4SB1OovKlUQ5arbiknUxR+3cXmRi090db9aWSq4+wLuqhpVOhnDTY83yKD9Ky8KDC9dQDgh4p0Ut6c+PpD2sbabooJBrDnOHqmE02TIRiipULVrRcAAtB72NBgVBebd4VTtxSZTxGvlnS/VCRbpN8lSr5p1Ou72I2nFhfrCuqmGRILwqw==', 'buyer_id': '2088102174924590', 'invoice_amount': '666.00', 'version': '1.0', 'notify_id': '11aab5323df78d1b3dba3e5aaf7636dkjy', 'fund_bill_list': '[{"amount":"666.00","fundChannel":"ALIPAYACCOUNT"}]', 'notify_type': 'trade_status_sync', 'out_trade_no': 'x21511506412.4733646', 'total_amount': '666.00', 'trade_status': 'TRADE_SUCCESS', 'trade_no': '2017112421001004590200343962', 'auth_app_id': '2016082500309412', 'receipt_amount': '666.00', 'point_amount': '0.00', 'app_id': '2016082500309412', 'buyer_pay_amount': '666.00', 'sign_type': 'RSA2', 'seller_id': '2088102172939262'}
            {'stade_status': "trade_success",'order':'x2123123123123'}
            """
            sign = post_dict.pop('sign', None)
            pay = AliPay(debug=True)
            status = pay.verify(post_dict, sign)
            if status:
                stade_status = post_dict['stade_status']
                out_trade_no = post_dict['out_trade_no']  # 订单号
                trade_no = post_dict['trade_no']  # 支付宝流水账号
                if status == 'TRADE_SUCCESS':
                    # 更新订单并写入第三个流水
                    models.Order.objects.filter(order_number=out_trade_no, status=1).update(status=0,
                                                                                            payment_number=trade_no)
                    response['code'] = 1000
        except Exception as e:
            response['msg'] = str(e)
        return Response(response)
