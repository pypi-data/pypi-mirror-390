from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from uzbekistan.dynamic_importer import (
    DynamicImporter,
    get_uzbekistan_setting,
    get_enabled_models,
    get_enabled_views,
    get_cache_settings,
    import_conditional_classes,
    DynamicImportError,
    validate_configuration,
)
from uzbekistan.models import Region, District, Village


class TestDynamicImporter(TestCase):
    def setUp(self):
        # Clear LRU caches
        get_enabled_models.cache_clear()
        get_enabled_views.cache_clear()
        get_cache_settings.cache_clear()
        DynamicImporter.clear_cache()

    @override_settings(UZBEKISTAN=None)
    def test_get_uzbekistan_setting_missing(self):
        """Test that missing UZBEKISTAN setting raises ImproperlyConfigured."""
        with self.assertRaises(ImproperlyConfigured) as context:
            get_uzbekistan_setting("models")
        self.assertIn("UZBEKISTAN setting is required", str(context.exception))

    def test_get_uzbekistan_setting_with_default(self):
        """Test getting setting with default value."""
        default = {"test": True}
        result = get_uzbekistan_setting("nonexistent", default)
        self.assertEqual(result, default)

    def test_get_enabled_models(self):
        """Test getting enabled models from settings."""
        with override_settings(
            UZBEKISTAN={"models": {"region": True, "district": False}}
        ):
            enabled = get_enabled_models()
            self.assertEqual(enabled, {"region"})

    def test_get_enabled_views(self):
        """Test getting enabled views from settings."""
        with override_settings(
            UZBEKISTAN={"views": {"region": True, "district": False}}
        ):
            enabled = get_enabled_views()
            self.assertEqual(enabled, {"region"})

    def test_import_conditional_classes_invalid_module(self):
        """Test importing from an invalid module."""
        with self.assertRaises(DynamicImportError) as context:
            list(import_conditional_classes("invalid.module", "views"))
        self.assertIn("Failed to import module", str(context.exception))

    def test_import_conditional_classes_missing_class(self):
        """Test importing non-existent class."""
        with override_settings(
            UZBEKISTAN={"views": {"nonexistent": True}, "models": {"nonexistent": True}}
        ):
            classes = list(import_conditional_classes("uzbekistan.views", "views"))
            self.assertEqual(len(classes), 0)

    def test_import_conditional_classes_disabled_model(self):
        """Test importing class with disabled model."""
        with override_settings(
            UZBEKISTAN={"views": {"region": True}, "models": {"region": False}}
        ):
            classes = list(import_conditional_classes("uzbekistan.views", "views"))
            self.assertEqual(len(classes), 0)

    def test_import_conditional_classes_success(self):
        """Test successful class import."""
        with override_settings(
            UZBEKISTAN={"views": {"region": True}, "models": {"region": True}}
        ):
            classes = list(import_conditional_classes("uzbekistan.views", "views"))
            self.assertTrue(len(classes) > 0)
            for cls in classes:
                self.assertTrue(hasattr(cls, "model"))
                self.assertTrue(cls.model in [Region, District, Village])

    def test_dynamic_importer_class_methods(self):
        """Test new DynamicImporter class methods."""
        with override_settings(
            UZBEKISTAN={
                "models": {"region": True, "district": False},
                "views": {"region": True},
            }
        ):
            # Test is_model_enabled
            self.assertTrue(DynamicImporter.is_model_enabled("region"))
            self.assertFalse(DynamicImporter.is_model_enabled("district"))

            # Test is_view_enabled
            self.assertTrue(DynamicImporter.is_view_enabled("region"))
            self.assertFalse(DynamicImporter.is_view_enabled("district"))

            # Test get_enabled_items
            models = DynamicImporter.get_enabled_items("models")
            self.assertEqual(models, {"region"})

            views = DynamicImporter.get_enabled_items("views")
            self.assertEqual(views, {"region"})

    def test_cache_config(self):
        """Test cache configuration."""
        cache_config = DynamicImporter.get_cache_config()
        self.assertTrue(hasattr(cache_config, "enabled"))
        self.assertTrue(hasattr(cache_config, "timeout"))
        self.assertTrue(hasattr(cache_config, "key_prefix"))

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # This should not raise any exception
        DynamicImporter.clear_cache()
