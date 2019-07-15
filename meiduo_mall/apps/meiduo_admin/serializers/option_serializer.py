from rest_framework import serializers

from goods.models import SpecificationOption, SPUSpecification


class OptSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value', 'spec', 'spec_id']


class OptionsepSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPUSpecification
        fields = '__all__'

