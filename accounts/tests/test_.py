from django.test import TestCase
from accounts.models import Account
from datetime import datetime, timezone

class AccountModelTest(TestCase):
    def setUp(self):
        # テストデータの作成
        self.account = Account.objects.create(
            email="test@example.com",
            name="Test User",
            password="securepassword",
            last_login_at=datetime(2024, 11, 18, tzinfo=timezone.utc),
        )

    def test_account_creation(self):
        """アカウントが正しく作成されることを確認"""
        self.assertEqual(self.account.email, "test@example.com")
        self.assertEqual(self.account.name, "Test User")
        self.assertEqual(self.account.password, "securepassword")
        self.assertEqual(self.account.last_login_at, datetime(2024, 11, 18, tzinfo=timezone.utc))
        self.assertIsNone(self.account.deleted_at)

    def test_str_representation(self):
        """__str__ メソッドが正しく動作することを確認"""
        self.assertEqual(str(self.account), "test@example.com")

    def test_account_soft_delete(self):
        """deleted_at を設定して論理削除を確認"""
        now = datetime.now(timezone.utc)
        self.account.deleted_at = now
        self.account.save()
        updated_account = Account.objects.get(id=self.account.id)
        self.assertEqual(updated_account.deleted_at, now)

    def test_account_unique_email(self):
        """email が一意であることを確認"""
        with self.assertRaises(Exception):
            Account.objects.create(
                email="test@example.com",
                name="Another User",
                password="anotherpassword",
            )
