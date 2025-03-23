"""URL configuration for the entire challengechat project.

This module contains the URL configuration for the entire challengechat project,
including routes for the Django admin interface and other app-level routes.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("chat.urls")),
]
