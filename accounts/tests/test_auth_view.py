from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Account


class AuthViewsTestCase(APITestCase):
    def setUp(self):
        # テスト用ユーザーを作成
        self.user = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword"),  # パスワードを暗号化して保存
            name="Test User",
        )
        self.login_url = "/api/accounts/login/"
        self.refresh_url = "/api/accounts/token/refresh/"
        self.logout_url = "/api/accounts/logout/"

    def test_login_success(self):
        """
        正しいメールアドレスとパスワードでログインできることをテスト
        """
        response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_credentials(self):
        """
        無効な資格情報でログインできないことをテスト
        """
        response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """
        存在しないユーザーでログインできないことをテスト
        """
        response = self.client.post(
            self.login_url,
            {"email": "nonexistent@example.com", "password": "securepassword"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        """
        正しいリフレッシュトークンでアクセストークンを再発行できることをテスト
        """
        # ログインしてリフレッシュトークンを取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.cookies.get("refresh_token").value

        # リフレッシュトークンでアクセストークンを再発行
        self.client.cookies["refresh_token"] = refresh_token  # Cookieを設定
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)

    def test_refresh_token_missing(self):
        """
        リフレッシュトークンがない場合にエラーを返すことをテスト
        """
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_refresh_token_invalid(self):
        """
        無効なリフレッシュトークンでエラーを返すことをテスト
        """
        self.client.cookies["refresh_token"] = "invalidtoken"
        response = self.client.post(self.refresh_url)
        print("??????")
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_logout_success(self):
        """
        正常にログアウトできることをテスト
        """
        # ログインしてトークンを取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # ログアウト
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")

        # Cookieが削除されていることを確認
        self.assertEqual(response.cookies.get("access_token").value, "")
        self.assertEqual(response.cookies.get("refresh_token").value, "")
