from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.pages import Mypage
from meiduo_admin.serializers.orders_serializer import *
from orders.models import OrderInfo


class OrdersViewSet(ModelViewSet):
    queryset = OrderInfo.objects.all().order_by('order_id')
    serializer_class = OrderSerializer
    pagination_class = Mypage

    def get_queryset(self, pk=None):
        keyword = self.request.query_params.get('keyword')
        if keyword is '' or keyword is None:
            return OrderInfo.objects.all().order_by('order_id')
        else:
            # 忽略大小写模糊过滤icontains
            return OrderInfo.objects.filter(order_id__icontains=keyword).order_by('order_id')


class OderView(ListAPIView):
    queryset = OrderInfo.objects.all().order_by('order_id')
    serializer_class = OrderSerializer

