from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'npi_db',
        'USER': 'npi',
        'PASSWORD': 'password',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}