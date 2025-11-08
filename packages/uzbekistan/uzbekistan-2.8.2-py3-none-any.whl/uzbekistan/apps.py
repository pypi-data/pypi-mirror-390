from django.apps import AppConfig
from django.conf import settings

from uzbekistan.dynamic_importer import DynamicImporter


class UzbekistanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uzbekistan"

    def ready(self):
        if not DynamicImporter.get_setting(
            "models", None
        ) or not DynamicImporter.get_setting("views", None):
            raise Exception("UZBEKISTAN settings is not configured properly.")

        enabled_models = settings.UZBEKISTAN["models"]
        dependencies = {"district": ["region"], "village": ["region", "district"]}

        # First pass: check dependencies for enabled models
        for model_name, is_enabled in enabled_models.items():
            if is_enabled and model_name in dependencies:
                # Check dependencies only if the model is enabled
                for dep in dependencies[model_name]:
                    if not enabled_models.get(dep, False):
                        raise NotImplementedError(
                            f"The '{model_name.title()}' model requires the '{dep.title()}' model to be enabled. "
                            f"Please ensure that '{dep.title()}' is set to True in the 'models' dictionary "
                            "of the UZBEKISTAN setting in your settings.py file."
                        )

        # Second pass: mark models as managed/abstract based on settings
        for model_name in ["region", "district", "village"]:
            model = self.get_model(model_name.title())
            is_enabled = enabled_models.get(model_name, False)
            model._meta.managed = is_enabled
            model._meta.abstract = not is_enabled
