from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from meiduo_admin.pages import Mypage
from goods.models import SKUImage, SKU
from meiduo_admin.serializers.image_serializer import ImageSerializer, SKUSimpleSerializer


class ImageViewSet(ModelViewSet):
    queryset = SKUImage.objects.all().order_by('id')
    serializer_class = ImageSerializer
    pagination_class = Mypage


class SkuSimpleView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer
