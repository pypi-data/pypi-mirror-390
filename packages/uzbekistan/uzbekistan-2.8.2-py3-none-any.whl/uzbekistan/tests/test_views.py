"""
Tests for uzbekistan app views.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from uzbekistan.models import Region, District, Village


class TestRegionAPI(APITestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name_uz="Toshkent", name_oz="Тошкент", name_ru="Ташкент", name_en="Tashkent"
        )
        self.url = reverse("region-list")

    def test_list_regions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name_uz"], "Toshkent")
