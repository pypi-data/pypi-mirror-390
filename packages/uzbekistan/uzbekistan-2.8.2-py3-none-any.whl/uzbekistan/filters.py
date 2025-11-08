from django.db.models import Q

from uzbekistan.models import Region, District, Village
from django_filters import (
    CharFilter,
    NumberFilter,
)
from django_filters.rest_framework import FilterSet


class BaseLocationFilterSet(FilterSet):
    """Base filter set with common functionality for all location models."""

    name = CharFilter(method="filter_by_name")

    @staticmethod
    def filter_by_name(queryset, name, value):
        """Optimized name filtering with case-insensitive search."""
        if not value:
            return queryset

        # Use icontains for better search results
        return queryset.filter(
            Q(name_uz__icontains=value)
            | Q(name_oz__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_en__icontains=value)
        ).distinct()


class RegionFilterSet(BaseLocationFilterSet):
    """Filter set for Region model."""

    class Meta:
        model = Region
        fields = ("name",)


class DistrictFilterSet(BaseLocationFilterSet):
    """Filter set for District model with region filtering."""

    region_id = NumberFilter(field_name="region__id")
    region_name = CharFilter(method="filter_by_region_name")

    @staticmethod
    def filter_by_region_name(queryset, name, value):
        """Filter districts by region name."""
        if not value:
            return queryset

        return queryset.filter(
            Q(region__name_uz__icontains=value)
            | Q(region__name_oz__icontains=value)
            | Q(region__name_ru__icontains=value)
            | Q(region__name_en__icontains=value)
        ).distinct()

    class Meta:
        model = District
        fields = ("name", "region_id", "region_name")


class VillageFilterSet(BaseLocationFilterSet):
    """Filter set for Village model with district and region filtering."""

    district_id = NumberFilter(field_name="district__id")
    district_name = CharFilter(method="filter_by_district_name")
    region_id = NumberFilter(field_name="district__region__id")
    region_name = CharFilter(method="filter_by_region_name")

    @staticmethod
    def filter_by_district_name(queryset, name, value):
        """Filter villages by district name."""
        if not value:
            return queryset

        return queryset.filter(
            Q(district__name_uz__icontains=value)
            | Q(district__name_oz__icontains=value)
            | Q(district__name_ru__icontains=value)
            | Q(district__name_en__icontains=value)
        ).distinct()

    @staticmethod
    def filter_by_region_name(queryset, name, value):
        """Filter villages by region name."""
        if not value:
            return queryset

        return queryset.filter(
            Q(district__region__name_uz__icontains=value)
            | Q(district__region__name_oz__icontains=value)
            | Q(district__region__name_ru__icontains=value)
            | Q(district__region__name_en__icontains=value)
        ).distinct()

    class Meta:
        model = Village
        fields = ("name", "district_id", "district_name", "region_id", "region_name")
