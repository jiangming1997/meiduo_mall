import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    cart_str = request.COOKIES.get('carts')
    if cart_str is None:
        return response

    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    redis_cont = get_redis_connection('carts')

    pl = redis_cont.pipeline()

    for sku_id in cart_dict:

        pl.hset('carts_%s' % request.user.id, sku_id, cart_dict[sku_id]['count'])
        if cart_dict[sku_id]['selected']:

            pl.sadd('selected_%s' % request.user.id, sku_id)
        else:
            pl.srem('selected_%s' % request.user.id, sku_id)

    pl.execute()

    response.delete_cookie('carts')

    return response
