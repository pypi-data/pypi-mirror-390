from django.urls import path

from uzbekistan.dynamic_importer import import_conditional_classes
from uzbekistan.views import BaseLocationView


def generate_url_patterns():
    """
    Generate URL patterns for all enabled location views.
    Returns a list of URL patterns with proper structure.
    """
    patterns = []
    views = import_conditional_classes("uzbekistan.views", "views")

    for view in views:
        if not isinstance(view, type) or not issubclass(view, BaseLocationView):
            continue

        # Generate URL pattern based on view configuration
        url_path = view.url_path
        url_name = view.url_name

        # Handle nested URLs (e.g., /regions/{region_id}/districts)
        if view.url_relation:
            url_pattern = f"{url_path}/<int:{view.url_relation}>"
        else:
            url_pattern = f"{url_path}"
        patterns.append(path(url_pattern, view.as_view(), name=url_name))

    return patterns


# URL patterns
urlpatterns = generate_url_patterns()
