import json
from django_redis import get_redis_connection
from django import http
from django.shortcuts import render

from meiduo_mall.utils.views import LoginRequiredView


class CouponPaymentView(LoginRequiredView):
    """优惠券页面"""

    def get(self, request):
        return render(request, 'coupon.html')

    def post(self, request):
        """

        :param: {conpons_1:{'coupon_id':100}}
        :return:
        """

        user = request.user
        query_dict = json.loads(request.body.decode())

        coupon_id = query_dict.get('coupon_id')

        redis_conn = get_redis_connection('coupon')

        redis_conn.hset('coupons_%s' % user.id, user.id, coupon_id)


        return http.JsonResponse({'code': 0, 'errmsg': '获取优惠券成功'})
