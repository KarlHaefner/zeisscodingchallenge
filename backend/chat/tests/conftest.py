"""Test configuration for the chat app.

This file configures the testing environment for the chat app.
It ensures that Django settings are properly loaded when using pytest.
    
The file is intended to be used with pytest-django, but it also serves as
documentation for the Django test runner setup.
    
Notes:
    - This file currently sets the default Django settings module.
    - Additional fixtures or plugins can be added as needed.
"""

import os

import django

# Set the default settings module for Django.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "challengechat.settings")

# Initialize Django.
django.setup()

# Additional pytest fixtures or configurations can be added here if necessary.
