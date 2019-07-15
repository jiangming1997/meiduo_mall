from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.channel_serializer import *
from meiduo_admin.pages import Mypage
from goods.models import GoodsChannel, GoodsChannelGroup


class ChannelViewSet(ModelViewSet):
    queryset = GoodsChannel.objects.all().order_by('id')
    serializer_class = ChannelSerializer
    pagination_class = Mypage


class ChannelGroupView(ListAPIView):
    queryset = GoodsChannelGroup.objects.all().order_by('id')
    serializer_class = ChannelGroupSerializer



