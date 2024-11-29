from django.contrib.auth.hashers import check_password
from django.test import TestCase

from accounts.serializer import AccountSerializer


class AccountSerializerTestCase(TestCase):
    def test_password_encryption_on_create(self):
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "plainpassword1",
        }
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            account = serializer.save()
            # 暗号化されたパスワードが保存されていることを確認
            self.assertTrue(check_password("plainpassword1", account.password))
        else:
            self.fail("Serializer validation failed")
