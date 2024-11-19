from .base import * # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "npi_db",
        "USER": "npi",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

SECURE_COOKIES = True