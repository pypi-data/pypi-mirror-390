from rest_framework.serializers import ModelSerializer

from uzbekistan.models import Region, District, Village


class RegionModelSerializer(ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name_uz", "name_oz", "name_ru", "name_en"]


class DistrictModelSerializer(ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name_uz", "name_oz", "name_ru", "name_en", "region"]


class VillageModelSerializer(ModelSerializer):
    class Meta:
        model = Village
        fields = ["id", "name_uz", "name_oz", "name_ru", "district"]
