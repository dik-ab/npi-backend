from django.contrib.auth.hashers import check_password
from django.db import models


class Account(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(null=False, blank=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    password = models.CharField(null=False, blank=False)
    secret_key = models.CharField(max_length=32, null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.email

    def check_password(self, raw_password):
        """
        パスワードを検証
        """
        return check_password(raw_password, self.password)
