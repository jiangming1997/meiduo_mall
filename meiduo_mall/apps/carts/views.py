import base64
import copy
import pickle

from django.shortcuts import render
from django.views import View
import json
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from carts import constants


class CartsView(View):

    def post(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('selected参数错误')

        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('错误的count')

        if request.user.is_authenticated:
            redis_cont = get_redis_connection('carts')

            pl = redis_cont.pipeline()

            pl.hincrby('carts_%s' % request.user.id, sku_id, count)

            if selected:
                pl.sadd('selected_%s' % request.user.id, sku_id)

            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts_dict = {}
            if carts_dict.get(sku_id):
                count += carts_dict.get(sku_id).get('count')

            carts_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            carts_cookies = base64.b64encode(pickle.dumps(carts_dict)).decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            response.set_cookie('carts', carts_cookies, max_age=constants.CARTS_COOKIE_EXPIRES)

            return response

    def get(self, request):

        user = request.user

        if user.is_authenticated:
            redis_cont = get_redis_connection('carts')
            skus_dict = redis_cont.hgetall(('carts_%s' % user.id))
            skus_list = redis_cont.smembers('selected_%s' % user.id)
            cart_dict = {}
            for sku_id in skus_dict:
                cart_dict[int(sku_id)] = {
                    'count': int(skus_dict[sku_id]),
                    'selected': sku_id in skus_list
                }

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return render(request, 'cart.html')

        cart_skus = []

        for sku_id in cart_dict:
            sku = SKU.objects.get(id=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),  # 为了方便前端解析此数据
                'count': cart_dict[sku_id]['count'],
                'selected': str(cart_dict[sku_id]['selected']),  # js中的bool  true,false
                'default_image_url': sku.default_image.url,
                'amount': str(sku.price*cart_dict[sku_id]['count'])
            })

        return render(request, 'cart.html', {'cart_skus': cart_skus})

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')

        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')
            # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
            # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        if request.user.is_authenticated:
            redis_cont = get_redis_connection('carts')
            pl = redis_cont.pipeline()
            pl.hset('carts_%s' % request.user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % request.user.id, sku_id)
            else:
                pl.srem('selected_%s' % request.user.id, sku_id)

            pl.execute()

            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,  # 为了方便前端解析此数据
                'count': count,
                'selected': selected,  # js中的bool  true,false
                'default_image_url': sku.default_image.url,
                'amount': sku.price*count
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        else:
            # 未登录用户，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'cookie数据没有获取到'})
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

    def delete(self, request):

        sku_id = json.loads(request.body.decode()).get('sku_id')

        if request.user.is_authenticated:

            redis_cont = get_redis_connection('carts')

            pl = redis_cont.pipeline()

            pl.hdel('carts_%s' % request.user.id, sku_id)
            pl.srem('selected_%s' % request.user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除商品成功'})

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'cookie数据没有获取到'})

            if sku_id in cart_dict:
                del cart_dict[sku_id]

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除商品成功'})

            if not cart_dict:
                response.delete_cookie('carts')
                return response

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response.set_cookie('carts', cart_str)

            return response


class CartsSelectedAllView(View):

    def put(self, request):
        selected = json.loads(request.body.decode()).get('selected')

        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('参数错误')

        if request.user.is_authenticated:
            redis_cont = get_redis_connection('carts')

            sku_ids = redis_cont.hgetall('carts_%s' % request.user.id).keys()

            if selected:
                redis_cont.sadd('selected_%s' % request.user.id, *sku_ids)
            else:
                redis_cont.delete('selected_%s' % request.user.id)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选商品成功'})

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'cookie数据没有获取到'})

            for sku_dict in cart_dict.values():
                sku_dict['selected'] = selected

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选商品成功'})

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response.set_cookie('carts', cart_str)

            return response


class CartsSimpleView(View):

    def get(self, request):

        user = request.user
        cart_skus = []

        if user.is_authenticated:
            redis_cont = get_redis_connection('carts')
            skus_dict = redis_cont.hgetall(('carts_%s' % user.id))
            skus_list = redis_cont.smembers('selected_%s' % user.id)
            cart_dict = {}
            for sku_id in skus_dict:
                cart_dict[int(sku_id)] = {
                    'count': int(skus_dict[sku_id]),
                    'selected': sku_id in skus_list
                }

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})

        for sku_id in cart_dict:
            sku = SKU.objects.get(id=sku_id)
            cart_skus.append({
                'name': sku.name,
                'count': cart_dict[sku_id]['count'],
                'default_image_url': sku.default_image.url,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})


class DeleteSelectedView(View):
    """一键清理购物车商品"""

    def delete(self, request):

        # 获取当前用户
        user = request.user
        # 判断是否登录用户
        if user.is_authenticated:
            # 创建连接redis数据库对象
            redis_conn = get_redis_connection('carts')
            # 获取购物车中的hash数据
            redis_carts = redis_conn.hgetall('carts_%s' % user.id)
            # 获取购物车中的set数据
            selected_ids = redis_conn.smembers('selected_%s' % user.id)
            # 对hash字典购物车数据进行过滤,只要勾选商品数据
            cart_dict = {}  # 用来包装所有勾选商品的sku_id,及count  {sku_id_16: count, sku_id_1: count}
            for sku_id_bytes in selected_ids:  # 遍历set集合,拿到勾选商品的sku_id
                cart_dict[int(sku_id_bytes)] = int(redis_carts[sku_id_bytes])
            # 根据sku_id查询到指定的sku模型
            skus = SKU.objects.filter(id__in=cart_dict.keys())
            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % user.id, *selected_ids)
            pl.delete('selected_%s' % user.id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除商品成功'})
        else:
            # 获取cookie中的carts
            cart_str = request.COOKIES.get('carts')
            # 判断cart_str是否存在
            if cart_str:
                # 转成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return http.HttpResponseForbidden('cookie没有获取到')
                # 遍历cookie字典将里面的selected全部改为前端传入的状态
            cart_dict_copy = copy.deepcopy(cart_dict)
            for sku_id in cart_dict_copy:
                if cart_dict[sku_id]['selected']:
                    del cart_dict[sku_id]

            # 判断sku_id是否存在字典中

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除商品成功', 'url': '/carts/'})
            # 如果购物车没有商品，直接删除cookie
            if not cart_dict:
                response.delete_cookie('carts')
                return response
            # 转成字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 设置cookie
            response.set_cookie('carts', cart_str)
            return response



