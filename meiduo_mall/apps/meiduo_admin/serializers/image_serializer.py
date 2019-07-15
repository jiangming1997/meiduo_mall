from django.conf import settings
from rest_framework import serializers

from goods.models import SKUImage, SKU
from fdfs_client.client import Fdfs_client


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'

    def create(self, validated_data):
        # 获取前端传来的logo文件
        file = validated_data.pop('image')
        # 读取logo文件赋值给content(二进制)
        content = file.read()
        # 创建fdfs的链接
        # conn = Fdfs_client('./meiduo_mall/utils/fastdfs/client.conf')
        conn = Fdfs_client(settings.FDFS_CONFPATH)
        # 上传二进制文件到fastdfs服务器中
        res = conn.upload_by_buffer(content)
        # 上传成功后会返回一个字典主要看：Remote file_id、Status
        # return dict
        # {
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        # }

        if res['Status'] == 'Upload successed.':
            validated_data['image'] = res['Remote file_id']
            return super().create(validated_data)
        else:
            raise serializers.ValidationError('上传失败')

    def update(self, instance, validated_data):
        # 获取前端传来的logo文件
        file = validated_data.pop('image')
        # 读取logo文件赋值给content(二进制)
        content = file.read()
        # 创建fdfs的链接
        # conn = Fdfs_client('./meiduo_mall/utils/fastdfs/client.conf')
        conn = Fdfs_client(settings.FDFS_CONFPATH)
        # 上传二进制文件到fastdfs服务器中
        res = conn.upload_by_buffer(content)
        # 上传成功后会返回一个字典主要看：Remote file_id、Status
        # return dict
        # {
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        # }

        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        # 更新文件id
        image = res['Remote file_id']
        # 对象的logo属性变更为新的logo
        instance.image = image
        # 保存
        instance.save()

        return instance


class SKUSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name']
