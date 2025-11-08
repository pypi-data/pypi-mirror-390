"""
Test URLs configuration for uzbekistan app.
"""

from django.urls import path, include

urlpatterns = [
    path("", include("uzbekistan.urls")),
]
