from django.conf.urls import url

from meiduo_admin.views.login_views import LoginView
from .views.login_views import jwt_payload_handler
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 添加购物车
    url(r'^authorizations/$', LoginView.as_view()),
]