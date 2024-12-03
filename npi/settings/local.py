import os

from .base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "npi-db"),
        "USER": os.getenv("DATABASE_USER", "npi"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "password"),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": os.getenv("DATABASE_PORT", "5435"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SECURE_COOKIES = False
HTTPONLY_COOKIES = False

SESSION_COOKIE_HTTPONLY = HTTPONLY_COOKIES
CSRF_COOKIE_HTTPONLY = HTTPONLY_COOKIES

CORS_ALLOW_ALL_ORIGINS = True
