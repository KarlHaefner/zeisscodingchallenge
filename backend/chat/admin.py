"""
Django admin configuration for the 'chat' application.

This module registers the UsageLog model so that system administrators
can view logs directly via the Django admin interface.

Notes:
    - This is optional but aids debugging or usage monitoring.
"""

from django.contrib import admin

from .models import UsageLog


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    """Configuration for displaying UsageLog entries in the Django admin."""

    list_display = (
        "timestamp",
        "model",
        "temperature",
    )

    # You can add filters, search fields, etc. here if desired, for example:
    # list_filter = ('model', 'timestamp')
    # search_fields = ('prompt_text', 'ai_response', 'trace_id')
