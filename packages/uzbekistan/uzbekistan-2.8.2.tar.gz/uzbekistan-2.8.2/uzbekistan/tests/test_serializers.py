import pytest
from django.test import TestCase
from uzbekistan.serializers import (
    RegionModelSerializer,
    DistrictModelSerializer,
    VillageModelSerializer,
)
from uzbekistan.models import Region, District, Village


class TestSerializers(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name_uz="Toshkent", name_oz="Тошкент", name_ru="Ташкент", name_en="Tashkent"
        )
        self.district = District.objects.create(
            region=self.region,
            name_uz="Yunusobod",
            name_oz="Юнусобод",
            name_ru="Юнусабад",
            name_en="Yunusabad",
        )
        self.village = Village.objects.create(
            district=self.district,
            name_uz="Mirobod",
            name_oz="Миробод",
            name_ru="Мирабад",
        )

    def test_region_serializer(self):
        serializer = RegionModelSerializer(self.region)
        data = serializer.data
        self.assertEqual(data["name_uz"], self.region.name_uz)
        self.assertEqual(data["name_oz"], self.region.name_oz)
        self.assertEqual(data["name_ru"], self.region.name_ru)
        self.assertEqual(data["name_en"], self.region.name_en)

    def test_district_serializer(self):
        serializer = DistrictModelSerializer(self.district)
        data = serializer.data
        self.assertEqual(data["name_uz"], self.district.name_uz)
        self.assertEqual(data["name_oz"], self.district.name_oz)
        self.assertEqual(data["name_ru"], self.district.name_ru)
        self.assertEqual(data["name_en"], self.district.name_en)
        self.assertEqual(data["region"], self.district.region.id)

    def test_village_serializer(self):
        serializer = VillageModelSerializer(self.village)
        data = serializer.data
        self.assertEqual(data["name_uz"], self.village.name_uz)
        self.assertEqual(data["name_oz"], self.village.name_oz)
        self.assertEqual(data["name_ru"], self.village.name_ru)
        self.assertEqual(data["district"], self.village.district.id)

    def test_region_serializer_create(self):
        data = {
            "name_uz": "Samarqand",
            "name_oz": "Самарқанд",
            "name_ru": "Самарканд",
            "name_en": "Samarkand",
        }
        serializer = RegionModelSerializer(data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        region = serializer.save()
        self.assertEqual(region.name_uz, data["name_uz"])
        self.assertEqual(region.name_oz, data["name_oz"])
        self.assertEqual(region.name_ru, data["name_ru"])
        self.assertEqual(region.name_en, data["name_en"])

    def test_district_serializer_create(self):
        data = {
            "name_uz": "Urgut",
            "name_oz": "Ургут",
            "name_ru": "Ургут",
            "name_en": "Urgut",
            "region": self.region.id,
        }
        serializer = DistrictModelSerializer(data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        district = serializer.save()
        self.assertEqual(district.name_uz, data["name_uz"])
        self.assertEqual(district.name_oz, data["name_oz"])
        self.assertEqual(district.name_ru, data["name_ru"])
        self.assertEqual(district.name_en, data["name_en"])
        self.assertEqual(district.region.id, data["region"])

    def test_village_serializer_create(self):
        data = {
            "name_uz": "Qo'shrabot",
            "name_oz": "Қўшработ",
            "name_ru": "Кушрабад",
            "district": self.district.id,
        }
        serializer = VillageModelSerializer(data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        village = serializer.save()
        self.assertEqual(village.name_uz, data["name_uz"])
        self.assertEqual(village.name_oz, data["name_oz"])
        self.assertEqual(village.name_ru, data["name_ru"])
        self.assertEqual(village.district.id, data["district"])
