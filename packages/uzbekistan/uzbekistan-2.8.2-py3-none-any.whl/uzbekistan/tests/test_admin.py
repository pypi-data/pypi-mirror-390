from django.contrib import admin
from django.test import TestCase

from uzbekistan.admin import RegionAdmin, DistrictAdmin, VillageAdmin
from uzbekistan.models import Region, District, Village


class TestAdmin(TestCase):
    def setUp(self):
        self.site = admin.site
        self.region = Region.objects.create(
            name_uz="Toshkent", name_oz="Тошкент", name_ru="Ташкент", name_en="Tashkent"
        )
        self.district = District.objects.create(
            name_uz="Yunusobod",
            name_oz="Юнусобод",
            name_ru="Юнусабад",
            name_en="Yunusabad",
            region=self.region,
        )
        self.village = Village.objects.create(
            name_uz="Mirobod",
            name_oz="Миробод",
            name_ru="Мирабад",
            district=self.district,
        )

    def test_region_admin(self):
        admin = RegionAdmin(Region, self.site)
        self.assertEqual(
            admin.list_display,
            ("name_uz", "name_oz", "name_ru", "name_en", "get_district_count"),
        )
        self.assertEqual(
            admin.search_fields, ("name_uz", "name_oz", "name_ru", "name_en")
        )

    def test_district_admin(self):
        admin = DistrictAdmin(District, self.site)
        self.assertEqual(
            admin.list_display,
            (
                "name_uz",
                "name_oz",
                "name_ru",
                "name_en",
                "get_region_name",
                "get_village_count",
            ),
        )
        self.assertEqual(
            admin.search_fields,
            (
                "name_uz",
                "name_oz",
                "name_ru",
                "name_en",
                "region__name_uz",
                "region__name_oz",
                "region__name_ru",
                "region__name_en",
            ),
        )
        self.assertEqual(admin.list_filter, ("region",))

    def test_village_admin(self):
        admin = VillageAdmin(Village, self.site)
        self.assertEqual(
            admin.list_display,
            ("name_uz", "name_oz", "name_ru", "get_district_name", "get_region_name"),
        )
        self.assertEqual(
            admin.search_fields,
            (
                "name_uz",
                "name_oz",
                "name_ru",
                "district__name_uz",
                "district__name_oz",
                "district__name_ru",
                "district__name_en",
                "district__region__name_uz",
                "district__region__name_oz",
                "district__region__name_ru",
                "district__region__name_en",
            ),
        )
        self.assertEqual(admin.list_filter, ("district", "district__region"))
