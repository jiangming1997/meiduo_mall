from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.sku_serializer import *
from meiduo_admin.pages import Mypage
from goods.models import SKU, GoodsCategory, SPU


class SKUgoodsViewSet(ModelViewSet):  # ListAPIView,
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = Mypage

    def get_queryset(self, pk=None):
        if self.action == 'categories':
            # 过滤出三级分类的选项
            return GoodsCategory.objects.filter(parent_id__gt=37).order_by('id')
        if self.action == 'goodsimple':
            # 获取商品信息
            return SPU.objects.all().order_by('id')
        if self.action == 'specs':
            # 根据商品过滤出该商品的规格选项
            return SPUSpecification.objects.filter(spu_id=pk).order_by('id')
        # if self.action == 'sku':
        #     # 根据商品过滤出该商品的规格选项
        #     return SKU.objects.all()

        # 获取请求头携带的关键字信息（搜索才有）
        keyword = self.request.query_params.get('keyword')
        if keyword is '' or keyword is None:
            return SKU.objects.all()
        else:
            # 忽略大小写模糊过滤icontains
            return SKU.objects.filter(name__icontains=keyword).order_by('id')

    def get_serializer_class(self):
        """根据action对应的方法，调用对应序列化器"""
        if self.action == "categories":
            return GoodsCategorySimpleSerializer
        if self.action == "goodsimple":
            return SPUSimpleSerializer
        if self.action == "specs":
            return SPUSpecSerializer
        # if self.action == "sku":
        #     return SKUSerializer

        return self.serializer_class

    # skus/categories/
    @action(methods=['get'], detail=False)
    def categories(self, request):
        """返回三级分类信息"""
        # cates = GoodsCategory.objects.filter(parent_id__gt=37)
        cates = self.get_queryset()
        # cates_serializer = GoodsCategorySimpleSerializer(cates, many=True)
        cates_serializer = self.get_serializer(cates, many=True)
        return Response(cates_serializer.data)

    # goods/simple/
    @action(methods=['get'], detail=False)
    def goodsimple(self, request):
        """返回三级分类信息"""
        simple = self.get_queryset()
        simple_serializer = self.get_serializer(simple, many=True)
        return Response(simple_serializer.data)

    # goods/(?P<pk>\d+)/specs/
    @action(methods=['get'], detail=False)
    def specs(self, request, pk):
        specs = self.get_queryset(pk=pk)
        specs_serializer = self.get_serializer(specs, many=True)
        return Response(specs_serializer.data)

    # meiduo_admin/skus/
    # @action(methods=['post'], detail=False)
    # def sku(self, request):
    #     sku = self.get_queryset()
    #     data = request.data
    #     sku_serializer = self.get_serializer(data=data)
    #     sku_serializer.is_valid()
    #     sku_serializer.save()
    #
    #     return Response(sku_serializer.data, status=status.HTTP_201_CREATED)

