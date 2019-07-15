from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response

from users.models import User
from meiduo_admin.pages import Mypage
from meiduo_admin.serializers.user_serializer import UserSerializer


class UserView(ListAPIView, CreateAPIView):  # GenericAPIView
    # 定义查询集
    queryset = User.objects.filter(is_staff=True)  # objects.all()
    # 定义序列化器
    serializer_class = UserSerializer
    # 定义分页器
    pagination_class = Mypage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(username__startswith=keyword)
        return self.queryset.all()

    # def get(self, request):
    #     return self.list(request)
    #     # 创建查询集对象
    #     user_qs = self.get_queryset()
    #     # 获取分页数
    #     page = self.paginate_queryset(user_qs)
    #
    #     if page:
    #         # 若有分页器则依据页数进行序列化
    #         page_serializer = self.get_serializer(page, many=True)
    #
    #         # 传入序列化后的数据由分页器进行响应
    #         return self.get_paginated_response(page_serializer.data)
    #     # 依据用户数据进行序列化
    #     us = self.get_serializer(user_qs, many=True)
    #     # 响应
    #     return Response(us.data)
