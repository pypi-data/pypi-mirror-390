import hashlib

from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from uzbekistan.dynamic_importer import DynamicImporter
from uzbekistan.filters import RegionFilterSet, DistrictFilterSet, VillageFilterSet
from uzbekistan.models import Region, District, Village, check_model
from uzbekistan.serializers import (
    RegionModelSerializer,
    DistrictModelSerializer,
    VillageModelSerializer,
)


class BaseLocationView(ListAPIView):
    """Base view for all location-based views with common functionality."""

    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    model: type[Region | District | Village] | None = None
    select_related_fields: list[str] = []
    prefetch_related_fields: list[str] = []
    # URL configuration
    url_path = ""
    url_name = ""
    url_relation = ""

    def get_queryset(self):
        check_model(self.model)
        queryset = self.model.objects.all()

        if hasattr(self, "url_relation") and self.url_relation:
            filter_kwargs = {self.url_relation: self.kwargs[self.url_relation]}
            queryset = queryset.filter(**filter_kwargs)

        # Optimize queries with select_related and prefetch_related
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset

    def get_permissions(self):
        """Override to allow unrestricted access."""
        use_authentication = DynamicImporter.get_setting("use_authentication", False)
        return [] if not use_authentication else super().get_permissions()

    def _generate_cache_key(self, request, kwargs):
        """Generate a cache key using hash."""
        # Get cache configuration
        cache_config = DynamicImporter.get_cache_config()

        query_string = str(sorted(request.query_params.items() | kwargs.items()))
        query_hash = hashlib.md5(
            query_string.encode(), usedforsecurity=False
        ).hexdigest()
        return f"{cache_config.key_prefix}_{self.__class__.__name__}_{query_hash}"

    def list(self, request, *args, **kwargs):
        cache_config = DynamicImporter.get_cache_config()

        if not cache_config.enabled:
            return super().list(request, *args, **kwargs)

        cache_key = self._generate_cache_key(request, kwargs)
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=cache_config.timeout)
        return response


class RegionListAPIView(BaseLocationView):
    serializer_class = RegionModelSerializer
    filterset_class = RegionFilterSet
    url_path = "regions"
    url_name = "region-list"
    url_relation = None
    model = Region
    select_related_fields = []


class DistrictListAPIView(BaseLocationView):
    serializer_class = DistrictModelSerializer
    filterset_class = DistrictFilterSet
    url_path = "districts"
    url_name = "district-list"
    url_relation = "region_id"
    model = District
    select_related_fields = ["region"]


class VillageListAPIView(BaseLocationView):
    serializer_class = VillageModelSerializer
    filterset_class = VillageFilterSet
    url_path = "villages"
    url_name = "village-list"
    url_relation = "district_id"
    model = Village
    select_related_fields = ["district", "district__region"]
