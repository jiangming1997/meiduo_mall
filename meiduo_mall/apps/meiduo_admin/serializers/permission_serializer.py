from django.contrib.auth.models import Permission, ContentType, Group
from users.models import User

from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['id', 'name']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

        # 重写父类方法，增加管理员权限属性

    def create(self, validated_data):
        # 添加管理员字段
        validated_data['is_staff'] = True
        # 调用父类方法创建管理员用户
        admin = super().create(validated_data)
        # 用户密码加密
        password = validated_data['password']
        admin.set_password(password)
        admin.save()

        return admin


