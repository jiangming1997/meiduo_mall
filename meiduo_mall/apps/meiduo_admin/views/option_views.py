from meiduo_admin.serializers.option_serializer import OptSerializer, OptionsepSerializer
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.pages import Mypage
from goods.models import SpecificationOption, SPUSpecification


class OptionsViewSet(ModelViewSet):
    queryset = SpecificationOption.objects.all().order_by('id')
    serializer_class = OptSerializer
    pagination_class = Mypage


class OptionsepViewSet(ModelViewSet):
    queryset = SPUSpecification.objects.all().order_by('id')
    serializer_class = OptionsepSerializer

