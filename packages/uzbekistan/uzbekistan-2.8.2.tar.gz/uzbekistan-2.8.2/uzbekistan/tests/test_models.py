"""
Tests for uzbekistan app models.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from uzbekistan.models import Region, District, Village


class TestRegion(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name_uz="Toshkent", name_oz="Тошкент", name_ru="Ташкент", name_en="Tashkent"
        )

    def test_region_creation(self):
        self.assertEqual(self.region.name_uz, "Toshkent")
        self.assertEqual(self.region.name_oz, "Тошкент")
        self.assertEqual(self.region.name_ru, "Ташкент")
        self.assertEqual(self.region.name_en, "Tashkent")

    def test_region_str(self):
        self.assertEqual(str(self.region), "Toshkent")

    def test_region_clean_validation(self):
        region = Region()
        with self.assertRaises(ValidationError):
            region.clean()

    def test_region_search_by_name(self):
        """Test the optimized search method."""
        # Create additional regions for testing
        Region.objects.create(
            name_uz="Samarqand",
            name_oz="Самарқанд",
            name_ru="Самарканд",
            name_en="Samarkand",
        )

        # Test search functionality
        results = Region.search_by_name("Tosh")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.first(), self.region)

        # Test case-insensitive search
        results = Region.search_by_name("tosh")
        self.assertEqual(len(results), 1)

        # Test search in different languages
        results = Region.search_by_name("Ташкент")
        self.assertEqual(len(results), 1)

    def test_region_unique_constraints(self):
        """Test that region names are unique."""
        with self.assertRaises(IntegrityError):
            Region.objects.create(
                name_uz="Toshkent",
                name_oz="Тошкент",
                name_ru="Ташкент",
                name_en="Tashkent",
            )


class TestDistrict(TestCase):
    def setUp(self):
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

    def test_district_creation(self):
        self.assertEqual(self.district.name_uz, "Yunusobod")
        self.assertEqual(self.district.name_oz, "Юнусобод")
        self.assertEqual(self.district.name_ru, "Юнусабад")
        self.assertEqual(self.district.name_en, "Yunusabad")
        self.assertEqual(self.district.region, self.region)

    def test_district_str(self):
        self.assertEqual(str(self.district), "Yunusobod")

    def test_district_clean_validation(self):
        district = District()
        with self.assertRaises(ValidationError):
            district.clean()

    def test_district_region_name_property(self):
        self.assertEqual(self.district.region_name, "Toshkent")

    def test_district_search_by_name(self):
        """Test the optimized search method."""
        # Create additional district for testing
        District.objects.create(
            name_uz="Chilonzor",
            name_oz="Чилонзор",
            name_ru="Чиланзар",
            name_en="Chilonzor",
            region=self.region,
        )

        # Test search functionality
        results = District.search_by_name("Yunus")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.first(), self.district)

        # Test search with region filter
        results = District.search_by_name("Yunus", region=self.region)
        self.assertEqual(len(results), 1)

        # Test search in different languages
        results = District.search_by_name("Юнусабад")
        self.assertEqual(len(results), 1)


class TestVillage(TestCase):
    def setUp(self):
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

    def test_village_creation(self):
        self.assertEqual(self.village.name_uz, "Mirobod")
        self.assertEqual(self.village.name_oz, "Миробод")
        self.assertEqual(self.village.name_ru, "Мирабад")
        self.assertEqual(self.village.district, self.district)

    def test_village_str(self):
        self.assertEqual(str(self.village), "Mirobod")

    def test_village_clean_validation(self):
        village = Village()
        with self.assertRaises(ValidationError):
            village.clean()

    def test_village_district_name_property(self):
        self.assertEqual(self.village.district_name, "Yunusobod")

    def test_village_region_name_property(self):
        self.assertEqual(self.village.region_name, "Toshkent")

    def test_village_search_by_name(self):
        """Test the optimized search method."""
        # Create additional village for testing
        Village.objects.create(
            name_uz="Navoiy",
            name_oz="Навоий",
            name_ru="Навои",
            district=self.district,
        )

        # Test search functionality
        results = Village.search_by_name("Miro")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.first(), self.village)

        # Test search with a district filter
        results = Village.search_by_name("Miro", district=self.district)
        self.assertEqual(len(results), 1)

        # Test search with region filter
        results = Village.search_by_name("Miro", region=self.region)
        self.assertEqual(len(results), 1)

        # Test search in different languages
        results = Village.search_by_name("Мирабад")
        self.assertEqual(len(results), 1)
