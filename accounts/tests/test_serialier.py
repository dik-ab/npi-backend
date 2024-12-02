from django.contrib.auth.hashers import check_password
from django.test import TestCase

from accounts.serializer import AccountSerializer, TOTPVerifySerializer


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


class TOTPVerifySerializerTestCase(TestCase):
    def test_totp_verification(self):
        data = {
            "code": "123456",
            "user_id": 1,
        }
        serializer = TOTPVerifySerializer(data=data)
        if serializer.is_valid():
            # TOTPコードの検証ロジックをテスト
            self.assertTrue(serializer.validated_data)
        else:
            self.fail("Serializer validation failed")
