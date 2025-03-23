"""
WSGI configuration for the challengechat project.

This module exposes the WSGI callable (application) for deployment with WSGI servers like gunicorn.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "challengechat.settings")
application = get_wsgi_application()
