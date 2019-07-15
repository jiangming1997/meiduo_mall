from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from meiduo_admin.pages import Mypage
from meiduo_admin.serializers.brand_serializer import BrandSerializer


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all().order_by('id')
    serializer_class = BrandSerializer
    pagination_class = Mypage
