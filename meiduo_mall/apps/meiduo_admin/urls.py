from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from meiduo_admin.views.brand_views import *
from meiduo_admin.views.channel_views import *
from meiduo_admin.views.image_views import *
from meiduo_admin.views.login_views import LoginView
from meiduo_admin.views.home_views import *
from meiduo_admin.views.option_views import *
from meiduo_admin.views.permission_views import *
from meiduo_admin.views.spec_views import *
from meiduo_admin.views.user_views import *
from meiduo_admin.views.sku_Views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.orders_views import *
from .views.login_views import jwt_payload_handler
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 添加购物车
    url(r'^authorizations/$', LoginView.as_view()),
    # 展示用户总数
    url(r'^statistical/total_count/$', UserTotalView.as_view()),
    # 日增用户
    url(r'^statistical/day_increment/$', UserDayCountView.as_view()),
    # 日活用户
    url(r'^statistical/day_active/$', UserActiveCountView.as_view()),
    # 日订单量
    url(r'^statistical/day_orders/$', UserOrderCountView.as_view()),
    # 月增用户
    url(r'^statistical/month_increment/$', UserMonthCountView.as_view()),
    # 分类商品访问量
    url(r'^statistical/goods_day_views/$', GoodsDayView.as_view()),
    # 用户管理
    url(r'^users/$', UserView.as_view()),

    # SKU
    # 商品管理
    url(r'^skus/$', SKUgoodsViewSet.as_view({'get': 'list', 'post': 'create'})),
    # 商品单独查询、修改、删除
    url(r'^skus/(?P<pk>\d+)/$', SKUgoodsViewSet.as_view({'get': 'retrieve',
                                                         'put': 'update',
                                                         'delete': 'destroy'})),
    # 获取3级商品
    url(r'^skus/categories/$', SKUgoodsViewSet.as_view({'get': 'categories'})),
    # 获取商品信息
    url(r'^goods/simple/$', SKUgoodsViewSet.as_view({'get': 'goodsimple'})),
    # 获取商品规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', SKUgoodsViewSet.as_view({'get': 'specs'})),

    # SPU
    # 显示全部商品
    url(r'^goods/$', SPUViewSet.as_view({'get': 'list', 'post': 'create'})),
    # 显示单独SPU、修改、删除
    url(r'^goods/(?P<pk>\d+)/$', SPUViewSet.as_view({'get': 'retrieve',
                                                     'put': 'update',
                                                     'delete': 'destroy'})),
    # 显示品牌
    url(r'^goods/brands/simple/$', BrandView.as_view()),
    # 显示一级分类
    url(r'^goods/channel/categories/$', CategoryView.as_view()),
    # 显示二三级分类
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', CategoryView.as_view()),

    # 规格
    url(r'^goods/specs/$', SpecsViewset.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/specs/(?P<pk>\d+)/$', SpecsViewset.as_view({'get': 'retrieve',
                                                             'put': 'update',
                                                             'delete': 'destroy'})),

    # 规格选项
    url(r'^specs/options/$', OptionsViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/specs/simple/$', OptionsepViewSet.as_view({'get': 'list'})),
    url(r'^specs/options/(?P<pk>\d+)/$', OptionsViewSet.as_view({'get': 'retrieve',
                                                                 'put': 'update',
                                                                 'delete': 'destroy'})),

    # 频道管理
    url(r'^goods/channels/$', ChannelViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/channels/(?P<pk>\d+)/$', ChannelViewSet.as_view({'get': 'retrieve',
                                                                  'put': 'update',
                                                                  'delete': 'destroy'})),
    url(r'^goods/categories/$', CategoryView.as_view()),
    url(r'^goods/channel_types/$', ChannelGroupView.as_view()),

    # 品牌管理
    url(r'^goods/brands/$', BrandViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^goods/brands/(?P<pk>\d+)/$', BrandViewSet.as_view({'get': 'retrieve',
                                                              'put': 'update',
                                                              'delete': 'destroy'})),




    # 照片管理
    url(r'^skus/images/$', ImageViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^skus/images/(?P<pk>\d+)/$', ImageViewSet.as_view({'get': 'retrieve',
                                                            'put': 'update',
                                                            'delete': 'destroy'})),
    url(r'^skus/simple/$', SkuSimpleView.as_view()),

    # 订单管理
    url(r'^orders/$', OrdersViewSet.as_view({'get': 'list'})),
    url(r'^orders/(?P<pk>\d+)/$', OrdersViewSet.as_view({'get': 'retrieve'})),
    url(r'^orders/(?P<pk>\d+)/status/$', OrdersViewSet.as_view({'patch': 'partial_update'})),


    # 权限管理
    url(r'^permission/perms/$', PermissionViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^permission/content_types/$', PermissionViewSet.as_view({'get': 'content_type'})),
    url(r'^permission/perms/(?P<pk>\d+)/$', PermissionViewSet.as_view({'delete': 'destroy'})),

    # 用户组管理
    url(r'^permission/groups/$', GroupViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^permission/groups/(?P<pk>\d+)/$', GroupViewSet.as_view({'get': 'retrieve',
                                                                   'put': 'update',
                                                                   'delete': 'destroy'})),
    url(r'^permission/simple/$', GroupViewSet.as_view({'get': 'simple'})),


    # 管理员管理
    url(r'^permission/admins/$', AdminViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^permission/admins/(?P<pk>\d+)/$', AdminViewSet.as_view({'get': 'retrieve',
                                                                   'put': 'update',
                                                                   'delete': 'destroy'})),
    url(r'^permission/groups/simple/$', AdminViewSet.as_view({'get': 'simple'})),


]

# router = SimpleRouter()
# # statistical/total_count/
# router.register(prefix="specs", viewset=OptionsViewSet, base_name="opt")
# router.register(prefix="goods/specs", viewset=OptionsViewSet, base_name="opt")
# urlpatterns += router.urls
