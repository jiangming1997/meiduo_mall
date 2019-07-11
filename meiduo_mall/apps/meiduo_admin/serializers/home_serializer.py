from rest_framework import serializers

from goods.models import GoodsVisitCount


class GoodsSerializer(serializers.ModelSerializer):
    # 序列化
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        
        model = GoodsVisitCount
        fields = ('count', 'category')
