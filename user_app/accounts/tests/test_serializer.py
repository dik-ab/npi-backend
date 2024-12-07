from django.contrib.auth.hashers import check_password
from django.test import TestCase

from user_app.accounts.serializer import AccountSerializer, TOTPVerifySerializer, PasswordResetSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer
from django.core import mail
from shared.models import Account
from django.utils.timezone import now
from datetime import timedelta


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


class PasswordResetSerializerTestCase(TestCase):
    def setUp(self):
        self.user = Account.objects.create(
            name="Test User",
            email="test@example.com",
            password="plainpassword1",
        )

    def test_password_reset_serializer_valid_email(self):
        """
        有効なアドレスの検証
        """
        data = {"email": "test@example.com"}
        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_reset_serializer_invalid_email(self):
        """
        無効なアドレスの検証
        """
        data = {"email": "invalid@example.com"}
        serializer = PasswordResetSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["email"][0], "このメールアドレスは登録されていません。"
        )

    def test_create_reset_token(self):
        """
        トークンの生成および保存検証
        """
        serializer = PasswordResetSerializer()
        raw_token = serializer.create_reset_token(self.user)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_token)
        self.assertIsNotNone(self.user.token_expiration)
        self.assertEqual(len(raw_token), 43)


class PasswordResetVerifySerializerTestCase(TestCase):
    def setUp(self):
        self.user = Account.objects.create(
            name="Test User",
            email="test@example.com",
            password="plainpassword1",
        )
        self.serializer = PasswordResetSerializer()

    def test_password_reset_confirm_serializer_valid_token(self):
        """
        有効なトークンの検証
        """
        raw_token = self.serializer.create_reset_token(self.user)
        data = {
            "email": "test@example.com",
            "token": raw_token,
        }
        serializer = PasswordResetVerifySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_reset_confirm_serializer_invalid_token(self):
        """
        無効なトークンの検証
        """
        data = {
            "email": "test@example.com",
            "token": "invalidtoken",
        }
        serializer = PasswordResetVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0], "無効なトークンです。")

    def test_password_reset_confirm_serializer_expired_token(self):
        """
        期限切れのトークンの検証
        """
        raw_token = self.serializer.create_reset_token(self.user)
        self.user.token_expiration = now() - timedelta(hours=1)
        self.user.save()
        data = {
            "email": "test@example.com",
            "token": raw_token,
        }
        serializer = PasswordResetVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0], "トークンが無効または期限切れです。")


class PasswordResetConfirmSerializerTestCase(TestCase):
    def setUp(self):
        self.user = Account.objects.create(
            name="Test User",
            email="test@example.com",
            password="plainpassword1",
        )
        self.serializer = PasswordResetSerializer()

    def test_password_reset_confirm_serializer_valid_token(self):
        """
        有効なトークンの検証
        """
        raw_token = self.serializer.create_reset_token(self.user)
        data = {
            "email": "test@example.com",
            "token": raw_token,
            "new_password": "plainpassword1",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_reset_confirm_serializer_invalid_token(self):
        """
        無効なトークンの検証
        """
        data = {
            "email": "test@example.com",
            "token": "invalidtoken",
            "new_password": "plainpassword1",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0], "無効なトークンです。")

    def test_password_reset_confirm_serializer_expired_token(self):
        """
        期限切れのトークンの検証
        """
        raw_token = self.serializer.create_reset_token(self.user)
        self.user.token_expiration = now() - timedelta(hours=1)
        self.user.save()
        data = {
            "email": "test@example.com",
            "token": raw_token,
            "new_password": "plainpassword1",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0], "トークンが無効または期限切れです。")

    def test_password_reset_confirm_serializer_save(self):
        """
        パスワードリセットの保存
        """
        raw_token = self.serializer.create_reset_token(self.user)
        data = {
            "email": "test@example.com",
            "token": raw_token,
            "new_password": "newpassword1",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            self.user.refresh_from_db()
            self.assertTrue(check_password("newpassword1", self.user.password))
            self.assertIsNone(self.user.reset_token)
            self.assertIsNone(self.user.token_expiration)
        else:
            self.fail("Serializer validation failed")
