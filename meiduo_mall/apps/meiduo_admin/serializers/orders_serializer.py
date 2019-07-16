from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class OrderSKUSeralizer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['name', 'default_image']


class OrderSKUsSeralizer(serializers.ModelSerializer):
    sku = OrderSKUSeralizer()

    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    skus = OrderSKUsSeralizer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
