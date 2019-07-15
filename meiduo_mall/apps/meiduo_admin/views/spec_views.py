from rest_framework.viewsets import ModelViewSet

from meiduo_admin.pages import Mypage
from goods.models import GoodsCategory, SPUSpecification
from meiduo_admin.serializers.spec_serializer import SPUSpecificationSerializer


class SpecsViewset(ModelViewSet):
    queryset = SPUSpecification.objects.all().order_by('id')
    serializer_class = SPUSpecificationSerializer
    pagination_class = Mypage
