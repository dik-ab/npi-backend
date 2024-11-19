from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password

class Account(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    last_login_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def check_password(self, raw_password):
        """
        パスワードを検証
        """
        return check_password(raw_password, self.password)
