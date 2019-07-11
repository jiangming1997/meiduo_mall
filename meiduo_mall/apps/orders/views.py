

import json
from _decimal import Decimal

from django import http
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django_redis import get_redis_connection

from coupon.models import Couponcard
from goods.models import SKU, IntegralGoods
from meiduo_mall.utils.views import LoginRequiredView
from users.models import Address
from .models import OrderGoods, OrderInfo
from meiduo_mall.utils.response_code import RETCODE


# logger = logging
class OrderSettlementView(LoginRequiredView):

    def get(self, request):
        user = request.user

        addresses = Address.objects.filter(user=user, is_deleted=False)

        if addresses.exists() is False:
            addresses = None

        redis_cont = get_redis_connection('carts')
        redis_conn = get_redis_connection('coupon')
        sku_list = redis_cont.smembers('selected_%s' % user.id)

        # 判断是否勾选优惠券，从redis数据获取判断

        # print(redis_dict)

        # 从redis数据库获取优惠券的数据
        # coupons_dict = redis_conn.hgetall('coupons_%s' % user.id)
        sku_dict = redis_cont.hgetall('carts_%s' % user.id)
        coupons_dict = redis_conn.hgetall('coupons_%s' % user.id)
        coupon_dict = {}  # 存储优惠券的键值

        for coupon_id in coupons_dict.values():
            coupon_dict[user.id] = int(coupon_id)
        # print(coupon_dict)
        coupon_id = coupon_dict.get(user.id)
        # print(coupon_id)
        cart = {}
        for sku_id in sku_list:
            cart[int(sku_id)] = int(sku_dict[sku_id])

        skus = SKU.objects.filter(id__in=sku_list)
        total_count = 0
        total_amount = Decimal(0.00)
        new_total_amount = Decimal(0.00)
        new_total_money = Decimal(0.00)
        # new_total_money

        selected_judge = 0
        choices_judge = 0
        total_integral = 0
        total_coupon = coupon_id
        total_integral_judge = 0

        for sku in skus:
            sku.integral = 0
            sku.new_price = sku.price

            goods_integral = IntegralGoods.objects.filter(sku=sku)

            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price
            if goods_integral:
                total_integral_judge += goods_integral[0].integral
                if request.user.integral >= total_integral_judge:
                    sku.integral = goods_integral[0].integral
                    sku.new_price = goods_integral[0].new_price
                    sku.new_amount = sku.count * sku.new_price
                    selected_judge += 1
                    total_integral += sku.integral * sku.count
                    new_total_amount += sku.new_amount
                else:
                    new_total_amount += sku.price * sku.count
                    sku.new_amount = sku.amount
            else:
                new_total_amount += sku.price
                sku.new_amount = sku.amount

            # 计算总数量和总金额
            total_count += sku.count
            total_amount += sku.count * sku.price
            new_counpon_amout = total_amount

            if coupon_id:
                new_counpon_amout = total_amount - coupon_id


            else:
                total_coupon = 0


        freight = Decimal(10.00)

        if skus.exists() is False:
            skus_length = 0
        else:
            skus_length = 1

        context = {
            'addresses': addresses
        }
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'new_total_amount': new_total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
            'new_payment_amount': new_total_amount + freight,
            'new_counpon_amout': new_counpon_amout + freight,
            'skus_length': skus_length,
            'selected_judge': selected_judge,
            'choices_judge': choices_judge,
            'total_integral': total_integral,
            'total_coupon':total_coupon
        }

        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredView):

    def post(self, request):
        user = request.user
        # 从redis获取优惠券的值
        redis_conn = get_redis_connection('coupon')
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        select_integral = json_dict.get('select_integral')

        coupons_dict = redis_conn.hgetall('coupons_%s' % user.id)
        coupon_dict = {}  # 存储优惠券的键值

        for coupon_id in coupons_dict.values():
            coupon_dict[user.id] = int(coupon_id)
        # print(coupon_dict)
        coupon_id = coupon_dict.get(user.id)
        user = request.user

        if all([address_id, pay_method]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('错误的address_id')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('错误的pay_method')

        # if isinstance(select_integral, bool) is False:
        #     return http.HttpResponseForbidden('错误的select_integral')

        with transaction.atomic():
            save_id = transaction.savepoint()

            order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

            order = OrderInfo.objects.create(
                order_id=order_id,
                user_id=user.id,
                address_id=address_id,
                total_count=0,
                total_amount=0,
                freight=10,
                pay_method=pay_method,
                status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
                else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            )

            redis_cont = get_redis_connection('carts')
            carts_dict = redis_cont.hgetall('carts_%s' % user.id)
            carts_list = redis_cont.smembers('selected_%s' % user.id)

            carts = {}

            for sku_id in carts_list:
                carts[int(sku_id)] = int(carts_dict[sku_id])

            for sku_id in carts.keys():
                while True:
                    sku = SKU.objects.get(id=sku_id)

                    origin_stock = sku.stock
                    origin_sales = sku.sales

                    buy_count = carts[sku_id]

                    if origin_stock < buy_count:
                        transaction.savepoint_rollback(save_id)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                    OrderGoods.objects.create(
                        order_id=order_id,
                        sku_id=sku_id,
                        count=buy_count,
                        price=sku.price
                    )

                    new_stock = origin_stock - buy_count
                    new_sales = origin_sales + buy_count

                    # sku.sales = new_sales
                    # sku.stock = new_stock
                    # sku.save()
                    reslut = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,sales=new_sales)
                    if reslut == 0:
                        continue
                    sku.spu.sales += buy_count
                    sku.spu.save()

                    order.total_count += buy_count
                    if select_integral == "false":
                        goods_integral = IntegralGoods.objects.filter(sku=sku)
                        if goods_integral:
                            sku.new_price = goods_integral[0].new_price
                            user.integral -= goods_integral[0].integral
                            user.save()
                        else:
                            # print(sku.price)
                            sku.new_price = sku.price
                            # print(12345)
                            # print(sku.new_price)

                        sku.amount = buy_count * sku.new_price
                    elif select_integral == "true":
                        order.total_amount -= coupon_id
                    else:
                        sku.amount = buy_count * sku.price
                        order.total_amount += sku.amount
                    break

            order.total_amount += order.freight
            # print(coupon_id)

            order.save()
        # except Exception as e:
            # logger.error(e)
            # return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            transaction.savepoint_commit(save_id)

        # pl = redis_cont.pipeline()
        # pl.hdel('carts_%s' % user.id, *carts_list)
        # pl.delete('selected_%s' % user.id, )
        #
        # pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(LoginRequiredView):

    def get(self, request):
        # 获取查询参数中的数据
        redis_conn = get_redis_connection('coupon')

        redis_conn.hdel('coupons_%s' % request.user.id, request.user.id)
        query_dict = request.GET
        order_id = query_dict.get('order_id')
        payment_amount = query_dict.get('payment_amount')
        # new_total_money = query_dict.get('new_total_money')
        # print(new_total_money)
        pay_method = query_dict.get('pay_method')

        # 校验
        try:
            OrderInfo.objects.get(order_id=order_id,pay_method=pay_method, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单有误')

        # 包装要拿到模板要进行渲染的数据
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        request.user.integral += (int(payment_amount)//10)
        request.user.save()

        return render(request, 'order_success.html', context)
