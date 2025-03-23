"""
Django application configuration for the `chat` app.

This class is automatically loaded by Django when the project starts.
It sets up metadata such as the app name.

Notes:
    - The `default_auto_field` is set to `django.db.models.BigAutoField` to ensure primary keys
      default to BigAutoField if not otherwise specified in models.
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """The configuration class for the 'chat' application.

    This class is responsible for registering the app with Django and setting
    app-specific settings.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"
