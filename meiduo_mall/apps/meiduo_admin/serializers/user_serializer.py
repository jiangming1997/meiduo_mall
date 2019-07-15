from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "mobile",
            "email",

            'password'
        ]

    # def create(self, validated_data):
    #     pass

    def create(self, validated_data):
        # validated_data['password'] = make_password(validated_data['password'])
        # validated_data['is_staff'] = True
        # return super().create(validated_data)
        
        # 创建超级用户
        # self.Meta.model => User
        # **validated_data => 解包
        return self.Meta.model.objects.create_superuser(**validated_data)

    # def validate(self, attrs):
    #     # print(attrs)
    #     # 获取密码数据
    #     password = attrs.get('password')
    #     # 进行加密
    #     password = make_password(password)
    #     # 重新讲加密后的密码添加回attrs
    #     attrs['password'] = password
    #     # 修改状态为'is_staff':True
    #     attrs['is_staff'] = True
    #     return attrs





