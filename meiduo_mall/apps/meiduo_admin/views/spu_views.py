from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_admin.pages import Mypage
from meiduo_admin.serializers.spu_serializer import *
from goods.models import SPUSpecification, SPU, Brand, GoodsCategory


class SPUViewSet(ModelViewSet):
    queryset = SPU.objects.all()
    serializer_class = SPUsepSerializer
    pagination_class = Mypage


class BrandView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CategoryView(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent=None)
    serializer_class = CategorySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk:
            return GoodsCategory.objects.filter(parent=pk)
        return GoodsCategory.objects.filter(parent=None)




