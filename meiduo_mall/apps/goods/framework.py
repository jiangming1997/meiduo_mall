import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")
django.setup()
from rest_framework import serializers

from goods.models import SKU


class SKUSerializer(serializers.Serializer):

    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=50, label='名称')
    caption = serializers.CharField(max_length=100, label='副标题')
    spu = serializers.PrimaryKeyRelatedField(read_only=True, label='商品')
    # serializers.PrimaryKeyRelatedField(label='图书', read_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True, label='从属类别')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, label='单价')
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, label='进价')
    market_price = serializers.DecimalField(max_digits=10, decimal_places=2, label='市场价')
    stock = serializers.IntegerField(default=0, label='库存', required=False)
    sales = serializers.IntegerField(default=0, label='销量', required=False)
    comments = serializers.IntegerField(default=0, label='评价数', required=False)
    is_launched = serializers.BooleanField(default=True, label='是否上架销售', required=False)
    # default_image = serializers.ImageField(max_length=200, default='', label='默认图片')

    def update(self, instance, validated_data):
        instance.price = validated_data.get('price')
        instance.save()
        return instance


sku = SKU.objects.get(id=2)
serializer = SKUSerializer(sku)
data = serializer.data
data['price'] = 11498.00
print(data)
data = {'name': 'Apple MacBook Pro 13.3英寸笔记本 深灰色', 'caption': '【全新2017款】MacBook Pro,一身才华，一触，即发 了解【黑五返场特惠】 更多产品请点击【美多官方Apple旗舰店】', 'price': 11498.0, 'cost_price': '10388.00', 'market_price': '13398.00', 'stock': 100, 'sales': 1, 'comments': 0, 'is_launched': True}

serializer1 = SKUSerializer(sku, data=data)
a = serializer1.is_valid()
print(a)
serializer1.save()
