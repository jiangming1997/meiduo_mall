from rest_framework import serializers

from goods.models import SKU, SKUSpecification, GoodsCategory, SPU, SPUSpecification, SpecificationOption


class SKUSpecSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ["spec_id", "option_id"]


class SKUSerializer(serializers.ModelSerializer):
    """
             获取sku表信息的序列化器
     """
    # 指定所关联的选项信息 关联嵌套返回
    specs = SKUSpecSerializer(many=True)

    # 指定分类信息
    category_id = serializers.IntegerField()
    # 关联嵌套返回
    category = serializers.StringRelatedField()
    # 指定所关联的spu表信息
    spu_id = serializers.IntegerField()
    # 序列化关联嵌套返回
    spu = serializers.StringRelatedField()

    class Meta:
        model = SKU  # SKU表中category外键关联了GoodsCategory分类表。spu外键关联了SPU商品表
        fields = '__all__'

    #     specs = SKUSpecSerializer(read_only=True, many=True)
    #     spu = serializers.StringRelatedField(read_only=True)
    #     spu_id = serializers.IntegerField()
    #     category = serializers.StringRelatedField(read_only=True)
    #     category_id = serializers.IntegerField()

    #
    #     class Meta:
    #         model = SKU
    #         fields = ["__all__"]
    # def create(self, validated_data):
    #     # 新建单一sku对象的时候，手动构建中间表数据，来保存规格和选项信息
    #     # [
    #     #      {"spec_id": 4, "option_id": 9},
    #     #      {}
    #     # ]
    #     specs = validated_data.pop('specs')
    #     # 创建从表数据对象之前，先创建主表sku对象
    #     instance = super().create(validated_data)
    #     for temp in specs:
    #         # temp: {"spec_id": 4, "option_id": 9}
    #         # sku_id = instance.id    spec_id=temp['spec_id']   option_id=temp['option_id']
    #         temp['sku_id'] = instance.id
    #         # 相当于create(sku_id = instance.id, spec_id=temp['spec_id'],option_id=temp['option_id'])
    #         SKUSpecification.objects.create(**temp)
    #     return instance
    def create(self, validated_data):
        # 新建单一sku对象的时候，手动构建中间表数据，来保存规格和选项信息
        # [
        #      {"spec_id": 4, "option_id": 9},
        #      {}
        # ]
        print(validated_data)
        specs = validated_data.pop("specs")

        # 创建从表数据对象之前，先创建主表sku对象
        instance = super().create(validated_data)

        # 遍历出有几个规格
        for temp in specs:
            # temp: {"spec_id": 4, "option_id": 9}
            # sku_id = instance.id    spec_id=temp['spec_id']   option_id=temp['option_id']
            temp['sku_id'] = instance.id
            # 相当于create(sku_id = instance.id, spec_id=temp['spec_id'],option_id=temp['option_id'])
            SKUSpecification.objects.create(**temp)

        return instance

    def update(self, instance, validated_data):
        specs = validated_data.pop('specs')

        # 原来的中间表数据
        # [
        #      {"spec_id": 4, "option_id": 9},
        #      {}
        # ]

        # [
        # {"spec_id": 4, "option_id": 8},
        # {},
        # ....
        # ]

        # 更新中间表
        # for temp in specs:
        #     # temp: {"spec_id": 4, "option_id": 8}
        #     # 获取中间表对象
        #     sku_spec = SKUSpecification.objects.get(sku_id=instance.id, spec_id=temp['spec_id'])
        #     sku_spec.option_id = temp['option_id']
        #     sku_spec.save()

        # 如果该sku对象，关联的spu更改了，规格变
        # 1、先删除中间表数据
        SKUSpecification.objects.filter(sku_id=instance.id).delete()
        # 2、根据新的规格选项区新建
        for temp in specs:
            # {"sku_id": instance.id, "spec_id": 4, "option_id": 8}
            temp['sku_id'] = instance.id
            SKUSpecification.objects.create(**temp)

        # 实现sku对象更新
        return super().update(instance, validated_data)




class GoodsCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ['id', 'name']


class SPUSpecOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecSerializer(serializers.ModelSerializer):
    spu = serializers.CharField()
    options = SPUSpecOptionSerializer(read_only=True, many=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'  # ['id', 'name']  #
