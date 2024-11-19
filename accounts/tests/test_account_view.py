from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.timezone import now
from accounts.models import Account

class AccountViewTestCase(APITestCase):
    def setUp(self):
        self.account1 = Account.objects.create(
            name="Test User 1",
            email="test1@example.com",
            password="securepassword1",
        )
        self.account2 = Account.objects.create(
            name="Test User 2",
            email="test2@example.com",
            password="securepassword2",
            deleted_at=now()
        )
        self.valid_account_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepassword3",
        }
        self.update_account_data = {
            "name": "Updated Name",
        }
        self.base_url = "/api/accounts/"

    def test_get_all_accounts(self):
        """
        削除されていないすべてのアカウントを取得
        """
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 削除されていないアカウントのみ

    def test_get_single_account_success(self):
        """
        特定のアカウントを正常に取得
        """
        response = self.client.get(f"{self.base_url}{self.account1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.account1.email)

    def test_get_single_account_not_found(self):
        """
        存在しないアカウントを取得
        """
        response = self.client.get(f"{self.base_url}999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_account_success(self):
        """
        新しいアカウントを正常に作成
        """
        response = self.client.post(self.base_url, data=self.valid_account_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.valid_account_data["email"])
        self.assertTrue(Account.objects.filter(email=self.valid_account_data["email"]).exists())

    def test_create_account_invalid_data(self):
        """
        無効なデータでアカウントを作成
        """
        invalid_data = {
            "name": "Invalid User",
            "email": "",  # 空のメールアドレス
            "password": "securepassword4",
        }
        response = self.client.post(self.base_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_update_account_success(self):
        """
        アカウント情報を正常に更新
        """
        response = self.client.put(f"{self.base_url}{self.account1.id}/", data=self.update_account_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.name, self.update_account_data["name"])

    def test_update_account_not_found(self):
        """
        存在しないアカウントの更新
        """
        response = self.client.put(f"{self.base_url}999/", data=self.update_account_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_success(self):
        """
        アカウントを正常に削除
        """
        response = self.client.delete(f"{self.base_url}{self.account1.id}/")
        print("!!!!!!")
        print(Account.objects.all())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.account1.refresh_from_db()
        self.assertIsNotNone(self.account1.deleted_at)

    def test_delete_account_not_found(self):
        """
        存在しないアカウントを削除
        """
        response = self.client.delete(f"{self.base_url}999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
