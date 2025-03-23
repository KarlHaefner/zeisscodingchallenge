#!/usr/bin/env python
"""Command-line utility for Django administrative tasks.

This file is the command-line utility for administrative tasks in Django.
It is responsible for executing commands like running the server, applying migrations,
creating superusers, etc.
"""

import os
import sys


def main() -> None:
    """Run administrative tasks for Django.

    Sets the default settings module and executes the command provided in sys.argv.
    
    Raises:
        ImportError: If Django is not installed or found.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "challengechat.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
