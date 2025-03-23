"""Django settings for the challengechat project.

This module defines the Django settings for the challengechat project.
It includes configurations for installed apps, middleware, database, and more.

Notes:
    - Reads environment variables from .env.local using python-dotenv if available.
    - Falls back to default values where environment variables are not set.
    - Includes minimal logging configuration (logs to console).
    - Configures a default database either from DATABASE_URL or uses local SQLite.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env.local if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env.local"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

# --------------------------------------------------------
# BASIC SETTINGS
# --------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "replace-this-with-a-real-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ["true", "1"]
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# --------------------------------------------------------
# APPLICATION DEFINITION
# --------------------------------------------------------
INSTALLED_APPS = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party apps
    "rest_framework",
    "corsheaders",
    # Local apps
    "chat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "chat.middleware.PdfFrameMiddleware",
]

ROOT_URLCONF = "challengechat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'chat', 'prompt_templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'chat.utils.template_loader.get_template_env',
        },
    },
]

WSGI_APPLICATION = "challengechat.wsgi.application"
# ASGI_APPLICATION = 'challengechat.asgi.application'  # If we integrate Channels or SSE in the future

# --------------------------------------------------------
# DATABASE CONFIG
# --------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    import re

    pattern = r"^(?P<engine>.+?)://(?P<user>.+?):(?P<password>.+?)@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<name>.+)$"
    match = re.match(pattern, DATABASE_URL)
    if not match:
        raise ValueError(
            "DATABASE_URL format is invalid. Expected postgres://USER:PASSWORD@HOST:PORT/NAME"
        )

    db_dict = match.groupdict()
    DB_ENGINE = db_dict["engine"]
    if "postgres" in DB_ENGINE:
        DB_ENGINE = "django.db.backends.postgresql"
    else:
        DB_ENGINE = "django.db.backends.postgresql"

    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": db_dict["name"],
            "USER": db_dict["user"],
            "PASSWORD": db_dict["password"],
            "HOST": db_dict["host"],
            "PORT": db_dict["port"] if db_dict["port"] else "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------
# STATIC FILES (CSS, JS, Images)
# --------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------------
# CORS HEADERS
# --------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # For development only; restrict in production
CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------------
# REST FRAMEWORK
# --------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# --------------------------------------------------------
# LOGGING
# --------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO" if not DEBUG else "DEBUG",
        },
    },
}

# --------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# --------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------
# AZURE OPENAI SETTINGS
# --------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


# --------------------------------------------------------
# FUNCIONALITY SETTINGS
# --------------------------------------------------------
USE_SUMMARIZATION = os.getenv("USE_SUMMARIZATION", "False").lower() in ["true", "1"]
