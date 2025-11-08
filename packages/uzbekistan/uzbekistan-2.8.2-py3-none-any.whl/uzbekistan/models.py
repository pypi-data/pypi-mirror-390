from django.db.models import Model, CharField, ForeignKey, CASCADE, Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from uzbekistan.dynamic_importer import DynamicImporter


class Region(Model):
    name_uz = CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Name in Uzbek language"),
    )
    name_oz = CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Name in Uzbek Cyrillic"),
    )
    name_ru = CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Name in Russian language"),
    )
    name_en = CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Name in English language"),
    )

    class Meta:
        db_table = "regions"
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __str__(self):
        return self.name_uz

    def clean(self):
        """Validate that all name fields are provided."""
        if not all([self.name_uz, self.name_oz, self.name_ru, self.name_en]):
            raise ValidationError(_("All name fields must be provided."))

    @classmethod
    def search_by_name(cls, query):
        """Optimized search method for finding regions by name."""
        return cls.objects.filter(
            Q(name_uz__icontains=query)
            | Q(name_oz__icontains=query)
            | Q(name_ru__icontains=query)
            | Q(name_en__icontains=query)
        ).distinct()


class District(Model):
    name_uz = CharField(
        max_length=255, db_index=True, help_text=_("Name in Uzbek language")
    )
    name_oz = CharField(
        max_length=255, db_index=True, help_text=_("Name in Uzbek Cyrillic")
    )
    name_ru = CharField(
        max_length=255, db_index=True, help_text=_("Name in Russian language")
    )
    name_en = CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Name in English language"),
    )
    region = ForeignKey(
        "uzbekistan.Region", on_delete=CASCADE, db_index=True, related_name="districts"
    )

    class Meta:
        db_table = "districts"
        unique_together = ("name_uz", "name_oz", "name_ru", "region")
        verbose_name = _("District")
        verbose_name_plural = _("Districts")

    def __str__(self):
        return self.name_uz

    def clean(self):
        """Validate that all name fields are provided."""
        if not all([self.name_uz, self.name_oz, self.name_ru, self.name_en]):
            raise ValidationError(_("All name fields must be provided."))

    @classmethod
    def search_by_name(cls, query, region=None):
        """Optimized search method for finding districts by name."""
        queryset = cls.objects.select_related("region").filter(
            Q(name_uz__icontains=query)
            | Q(name_oz__icontains=query)
            | Q(name_ru__icontains=query)
            | Q(name_en__icontains=query)
        )
        if region:
            queryset = queryset.filter(region=region)
        return queryset.distinct()

    @property
    def region_name(self):
        """Get the name of the related region."""
        return self.region.name_uz


class Village(Model):
    name_uz = CharField(
        max_length=255, db_index=True, help_text=_("Name in Uzbek language")
    )
    name_oz = CharField(
        max_length=255, db_index=True, help_text=_("Name in Uzbek Cyrillic")
    )
    name_ru = CharField(
        max_length=255, db_index=True, help_text=_("Name in Russian language")
    )
    district = ForeignKey(
        "uzbekistan.District", on_delete=CASCADE, db_index=True, related_name="villages"
    )

    class Meta:
        db_table = "villages"
        unique_together = ("name_uz", "name_oz", "name_ru", "district")
        verbose_name = _("Village")
        verbose_name_plural = _("Villages")

    def __str__(self):
        return self.name_uz

    def clean(self):
        """Validate that all name fields are provided."""
        if not all([self.name_uz, self.name_oz, self.name_ru]):
            raise ValidationError(_("All name fields must be provided."))

    @classmethod
    def search_by_name(cls, query, district=None, region=None):
        """Optimized search method for finding villages by name."""
        queryset = cls.objects.select_related("district", "district__region").filter(
            Q(name_uz__icontains=query)
            | Q(name_oz__icontains=query)
            | Q(name_ru__icontains=query)
        )
        if district:
            queryset = queryset.filter(district=district)
        if region:
            queryset = queryset.filter(district__region=region)
        return queryset.distinct()

    @property
    def district_name(self):
        """Get the name of the related district."""
        return self.district.name_uz

    @property
    def region_name(self):
        """Get the name of the related region."""
        return self.district.region_name


def check_model(model):
    """
    Check if the model is enabled in settings and its dependencies are met.

    Args:
        model: Django model class to check

    Raises:
        NotImplementedError: If model is not enabled or dependencies are not met
    """
    model_name = model.__name__.lower()

    # Check if model is abstract
    if model._meta.abstract:
        raise NotImplementedError(f"Abstract model '{model}' cannot be used directly.")

    # Check if model is enabled
    if not DynamicImporter.is_model_enabled(model_name):
        raise NotImplementedError(
            f"The model '{model}' is not enabled in the current configuration. "
            "Please check that this model is set to True in the 'models' dictionary "
            "of the UZBEKISTAN setting in your settings.py file."
        )

    # Check dependencies
    dependencies = {"district": ["region"], "village": ["region", "district"]}

    if model_name in dependencies:
        for dep in dependencies[model_name]:
            if not DynamicImporter.is_model_enabled(dep):
                raise NotImplementedError(
                    f"The '{model.__name__}' model requires the '{dep.title()}' model to be enabled. "
                    "Please ensure that '{dep.title()}' is set to True in the 'models' dictionary "
                    "of the UZBEKISTAN setting in your settings.py file."
                )
