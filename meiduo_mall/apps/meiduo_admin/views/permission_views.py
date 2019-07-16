from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from meiduo_admin.pages import Mypage
from django.contrib.auth.models import Permission, ContentType, Group
from users.models import User

from meiduo_admin.serializers.permission_serializer import *


class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer
    pagination_class = Mypage

    def content_type(self, request):
        content = ContentType.objects.all().order_by('id')
        content_sr = ContentTypeSerializer(content, many=True)
        return Response(content_sr.data)


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    pagination_class = Mypage

    def simple(self, request):
        simple = Permission.objects.all().order_by('id')
        simple_sr = PermissionSerializer(simple, many=True)
        return Response(simple_sr.data)


class AdminViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = Mypage

    def simple(self, request):
        simple = Group.objects.all().order_by('id')
        simple_sr = GroupSerializer(simple, many=True)
        return Response(simple_sr.data)
