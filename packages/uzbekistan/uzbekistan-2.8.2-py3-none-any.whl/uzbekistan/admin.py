from django.contrib import admin
from django.contrib.admin import ModelAdmin

from uzbekistan.models import Region, District, Village
from uzbekistan.dynamic_importer import DynamicImporter

if DynamicImporter.is_model_enabled("region"):

    @admin.register(Region)
    class RegionAdmin(ModelAdmin):
        list_display = (
            "name_uz",
            "name_oz",
            "name_ru",
            "name_en",
            "get_district_count",
        )
        search_fields = ("name_uz", "name_oz", "name_ru", "name_en")
        sortable_by = ("name_uz", "name_oz", "name_ru", "name_en")
        list_per_page = 50

        def get_district_count(self, obj):
            """Get the count of districts in this region."""
            return obj.districts.count()

        get_district_count.short_description = "Districts"
        get_district_count.admin_order_field = "districts__count"


if DynamicImporter.is_model_enabled("district"):

    @admin.register(District)
    class DistrictAdmin(ModelAdmin):
        list_display = (
            "name_uz",
            "name_oz",
            "name_ru",
            "name_en",
            "get_region_name",
            "get_village_count",
        )
        search_fields = (
            "name_uz",
            "name_oz",
            "name_ru",
            "name_en",
            "region__name_uz",
            "region__name_oz",
            "region__name_ru",
            "region__name_en",
        )
        sortable_by = ("name_uz", "name_oz", "name_ru", "name_en", "region")
        list_filter = ("region",)
        save_on_top = True
        list_per_page = 50
        list_select_related = ("region",)

        def get_region_name(self, obj):
            return obj.region.name_uz

        get_region_name.short_description = "Region"
        get_region_name.admin_order_field = "region__name_uz"

        def get_village_count(self, obj):
            """Get the count of villages in this district."""
            return obj.villages.count()

        get_village_count.short_description = "Villages"
        get_village_count.admin_order_field = "villages__count"


if DynamicImporter.is_model_enabled("village"):

    @admin.register(Village)
    class VillageAdmin(ModelAdmin):
        list_display = (
            "name_uz",
            "name_oz",
            "name_ru",
            "get_district_name",
            "get_region_name",
        )
        search_fields = (
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
        )
        sortable_by = ("name_uz", "name_oz", "name_ru", "district")
        list_filter = ("district", "district__region")
        save_on_top = True
        list_per_page = 50
        list_select_related = ("district", "district__region")

        def get_district_name(self, obj):
            return obj.district.name_uz

        get_district_name.short_description = "District"
        get_district_name.admin_order_field = "district__name_uz"

        def get_region_name(self, obj):
            return obj.district.region.name_uz

        get_region_name.short_description = "Region"
        get_region_name.admin_order_field = "district__region__name_uz"
