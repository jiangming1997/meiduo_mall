from django.conf.urls import url

from meiduo_admin.views.login_views import LoginView
from meiduo_admin.views.home_views import *
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

]