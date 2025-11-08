"""
Tests for uzbekistan app configuration.
"""

from django.test import TestCase, override_settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from uzbekistan.apps import UzbekistanConfig
import uzbekistan


class TestUzbekistanConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Store the original app registry
        cls._original_apps = apps.app_configs.copy()
        cls._original_ready = apps.ready

    def setUp(self):
        self.app_config = apps.get_app_config("uzbekistan")

    def tearDown(self):
        # Reset app registry state after each test
        apps.app_configs = self._original_apps.copy()
        apps.ready = self._original_ready
        # Re-initialize the app config
        self.app_config = UzbekistanConfig("uzbekistan", uzbekistan)
        apps.app_configs["uzbekistan"] = self.app_config

    def test_app_config_attributes(self):
        """Test that app config has correct attributes."""
        self.assertEqual(self.app_config.name, "uzbekistan")
        self.assertEqual(
            self.app_config.default_auto_field, "django.db.models.BigAutoField"
        )

    @override_settings(
        UZBEKISTAN={
            "models": {"region": False, "district": True, "village": True},
            "views": {"region": True},
        }
    )
    def test_ready_with_disabled_model(self):
        """Test that trying to enable a model with disabled dependencies raises NotImplementedError."""
        with self.assertRaisesMessage(
            NotImplementedError,
            "The 'District' model requires the 'Region' model to be enabled. Please ensure that 'Region' is set to True in the 'models' dictionary of the UZBEKISTAN setting in your settings.py file.",
        ):
            self.app_config.ready()

    @override_settings(
        UZBEKISTAN={
            "models": {"region": True, "district": False, "village": True},
            "views": {"region": True},
        }
    )
    def test_ready_with_disabled_dependent_model(self):
        """Test that trying to enable a model with disabled dependencies raises NotImplementedError."""
        with self.assertRaisesMessage(
            NotImplementedError,
            "The 'Village' model requires the 'District' model to be enabled. Please ensure that 'District' is set to True in the 'models' dictionary of the UZBEKISTAN setting in your settings.py file.",
        ):
            self.app_config.ready()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Restore the original app registry
        apps.app_configs = cls._original_apps.copy()
        apps.ready = cls._original_ready
