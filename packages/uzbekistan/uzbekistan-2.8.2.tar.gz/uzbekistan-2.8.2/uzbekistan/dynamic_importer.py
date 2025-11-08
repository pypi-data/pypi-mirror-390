from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from typing import Generator, Type, Any, Dict, Set

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class CacheConfig:
    """Cache configuration dataclass."""

    enabled: bool = True
    timeout: int = 3600
    key_prefix: str = "uzbekistan"


class DynamicImportError(Exception):
    """Custom exception for dynamic import errors."""

    pass


class CacheIncorrectlyConfigured(Exception):
    """Custom exception for cache configuration errors."""

    pass


class DynamicImporter:
    """
    Dynamic importer for the package.

    This class handles all dynamic importing logic with proper caching,
    error handling, and type safety.
    """

    # Class-level cache for imported modules
    _module_cache: Dict[str, Any] = {}

    @staticmethod
    def get_setting(setting_name: str, default: Any = None) -> Any:
        """
        Get a setting from UZBEKISTAN settings with proper error handling.

        Args:
            setting_name: Name of the setting to get
            default: Default value if setting doesn't exist

        Returns:
            The setting value or default

        Raises:
            ImproperlyConfigured: If UZBEKISTAN setting is not configured
        """
        if not hasattr(settings, "UZBEKISTAN") or settings.UZBEKISTAN is None:
            raise ImproperlyConfigured(
                "The UZBEKISTAN setting is required. Please add it to your settings.py file."
            )
        return settings.UZBEKISTAN.get(setting_name, default)

    @classmethod
    @lru_cache(maxsize=1)
    def get_cache_config(cls) -> CacheConfig:
        """
        Get cache configuration with caching.

        Returns:
            CacheConfig object with cache settings
        """
        cache_settings = cls.get_setting(
            "cache", {"enabled": True, "timeout": 3600, "key_prefix": "uzbekistan"}
        )
        return CacheConfig(**cache_settings)

    @classmethod
    @lru_cache(maxsize=1)
    def get_enabled_items(cls, item_type: str) -> Set[str]:
        """
        Get a set of enabled items (models/views) from settings.

        Args:
            item_type: Type of items ('models' or 'views')

        Returns:
            Set of enabled item names
        """
        items = cls.get_setting(item_type, {})
        return {name.lower() for name, enabled in items.items() if enabled}

    @classmethod
    def validate_cache(cls) -> None:
        """
        Validate cache configuration and functionality.

        Raises:
            CacheIncorrectlyConfigured: If cache is not working properly
        """
        cache_config = cls.get_cache_config()

        if not cache_config.enabled:
            return

        try:
            test_key = f"{cache_config.key_prefix}_health_check"
            test_value = "alive"

            # Test cache functionality
            cache.set(test_key, test_value, timeout=60)
            cache_data = cache.get(test_key)
            cache.delete(test_key)

            if cache_data != test_value:
                raise CacheIncorrectlyConfigured("Cache is not configured correctly.")

        except Exception as e:
            raise CacheIncorrectlyConfigured(f"Cache health check failed: {e}")

    @classmethod
    def get_module(cls, module_name: str) -> Any:
        """
        Get module with caching to avoid repeated imports.

        Args:
            module_name: Full module path to import

        Returns:
            Imported module object

        Raises:
            DynamicImportError: If import fails
        """
        if module_name not in cls._module_cache:
            try:
                cls._module_cache[module_name] = import_module(module_name)
            except ImportError as e:
                raise DynamicImportError(f"Failed to import module {module_name}: {e}")

        return cls._module_cache[module_name]

    @classmethod
    def get_class_name(cls, item_name: str, class_type: str) -> str:
        """
        Generate class name based on item name and type.

        Args:
            item_name: Name of the item (e.g., 'region')
            class_type: Type of class ('views' or 'models')

        Returns:
            Generated class name
        """
        if class_type == "views":
            return f"{item_name.title()}ListAPIView"
        elif class_type == "models":
            return item_name.title()
        else:
            raise ValueError(f"Invalid class_type: {class_type}")

    @classmethod
    def validate_class(cls, class_obj: Type[Any], class_type: str) -> bool:
        """
        Validate that a class meets the requirements.

        Args:
            class_obj: Class object to validate
            class_type: Type of class ('views' or 'models')

        Returns:
            True if the class is valid, False otherwise
        """
        if class_type == "views":
            # Views must have a model attribute
            return hasattr(class_obj, "model")
        elif class_type == "models":
            # Models must be Django models
            return hasattr(class_obj, "_meta")
        return False

    @classmethod
    def check_dependencies(cls, class_obj: Type[Any], class_type: str) -> bool:
        """
        Check if class dependencies are met.

        Args:
            class_obj: Class object to check
            class_type: Type of class ('views' or 'models')

        Returns:
            True if dependencies are met, False otherwise
        """
        if class_type == "views" and hasattr(class_obj, "model"):
            model_name = class_obj.model.__name__.lower()
            enabled_models = cls.get_enabled_items("models")
            return model_name in enabled_models
        return True

    @classmethod
    def import_classes(
        cls, module_name: str, class_type: str
    ) -> Generator[Type[Any], None, None]:
        """
        Dynamically import classes based on settings configuration.

        Args:
            module_name: Full module path to import from
            class_type: Type of classes to import ('views' or 'models')

        Yields:
            Imported class objects that meet all requirements

        Raises:
            DynamicImportError: If import fails or class not found
        """
        # Get enabled items
        enabled_items = cls.get_enabled_items(class_type)

        if not enabled_items:
            return

        # Get module
        module = cls.get_module(module_name)

        for item_name in enabled_items:
            try:
                class_name = cls.get_class_name(item_name, class_type)

                # Check if class exists in module
                if not hasattr(module, class_name):
                    continue

                class_obj = getattr(module, class_name)

                # Validate class
                if not cls.validate_class(class_obj, class_type):
                    continue

                # Check dependencies
                if not cls.check_dependencies(class_obj, class_type):
                    continue

                yield class_obj

            except AttributeError as e:
                raise DynamicImportError(
                    f"Failed to import {class_name} from {module_name}: {e}"
                )
            except Exception as e:
                raise DynamicImportError(
                    f"Unexpected error importing {class_name} from {module_name}: {e}"
                )

    @classmethod
    def is_model_enabled(cls, model_name: str) -> bool:
        """Check if a specific model is enabled."""
        return model_name.lower() in cls.get_enabled_items("models")

    @classmethod
    def is_view_enabled(cls, view_name: str) -> bool:
        """Check if a specific view is enabled."""
        return view_name.lower() in cls.get_enabled_items("views")

    @classmethod
    def get_enabled_models_list(cls) -> list[str]:
        """Get a list of enabled model names."""
        return list(cls.get_enabled_items("models"))

    @classmethod
    def get_enabled_views_list(cls) -> list[str]:
        """Get a list of enabled view names."""
        return list(cls.get_enabled_items("views"))

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches (useful for testing)."""
        cls.get_cache_config.cache_clear()
        cls.get_enabled_items.cache_clear()
        cls._module_cache.clear()


# Backward compatibility functions (kept for existing code)
def get_uzbekistan_setting(setting_name: str, default: Any = None) -> Any:
    """Backward compatibility function."""
    return DynamicImporter.get_setting(setting_name, default)


@lru_cache(maxsize=32)
def get_enabled_models() -> Set[str]:
    """Backward compatibility function."""
    return DynamicImporter.get_enabled_items("models")


@lru_cache(maxsize=32)
def get_enabled_views() -> Set[str]:
    """Backward compatibility function."""
    return DynamicImporter.get_enabled_items("views")


@lru_cache(maxsize=32)
def get_cache_settings() -> Dict[str, Any]:
    """Backward compatibility function."""
    cache_config = DynamicImporter.get_cache_config()
    return {
        "enabled": cache_config.enabled,
        "timeout": cache_config.timeout,
        "key_prefix": cache_config.key_prefix,
    }


def import_conditional_classes(
    module_name: str, class_type: str
) -> Generator[Type[Any], None, None]:
    """Backward compatibility function."""
    return DynamicImporter.import_classes(module_name, class_type)


# Convenience functions for common operations
def get_enabled_models_list() -> list[str]:
    """Get a list of enabled model names."""
    return DynamicImporter.get_enabled_models_list()


def get_enabled_views_list() -> list[str]:
    """Get a list of enabled view names."""
    return DynamicImporter.get_enabled_views_list()


def is_model_enabled(model_name: str) -> bool:
    """Check if a specific model is enabled."""
    return DynamicImporter.is_model_enabled(model_name)


def is_view_enabled(view_name: str) -> bool:
    """Check if a specific view is enabled."""
    return DynamicImporter.is_view_enabled(view_name)


def validate_configuration() -> None:
    """Validate the entire configuration."""
    DynamicImporter.validate_cache()

    # Check that at least one model is enabled
    if not get_enabled_models():
        raise ImproperlyConfigured(
            "At least one model must be enabled in UZBEKISTAN settings."
        )

    # Check dependencies
    enabled_models = get_enabled_models()
    if "district" in enabled_models and "region" not in enabled_models:
        raise ImproperlyConfigured(
            "District model requires Region model to be enabled."
        )

    if "village" in enabled_models and (
        "region" not in enabled_models or "district" not in enabled_models
    ):
        raise ImproperlyConfigured(
            "Village model requires both Region and District models to be enabled."
        )
