from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.test import APITestCase
from npi.utils import ERROR_MESSAGES
from django.urls import reverse

from accounts.models import Account


class AuthViewsTestCase(APITestCase):

    def setUp(self):
        # テスト用ユーザーを作成
        self.user = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),  # パスワードを暗号化して保存
            name="Test User",
        )
        self.login_url = reverse("login")
        self.refresh_url = reverse("refresh")
        self.logout_url = reverse("logout")

    def test_login_success(self):
        """
        正しいメールアドレスとパスワードでログインできることをテスト
        """
        response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_bad_request(self):
        """
        リクエストが不正な場合に、400エラーを返すことをテスト
        """
        response = self.client.post(self.login_url, {"test": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = ERROR_MESSAGES["400_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_login_unauthorized(self):
        """
        認証に失敗した場合に、401エラーを返すことをテスト
        """
        response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_login_not_found(self):
        """
        DBにアカウントが一件も存在しない場合に、401エラーを返すことをテスト
        """
        # アカウントを全削除
        Account.objects.all().delete()
        response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "wrongpassword1"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_refresh_token_success(self):
        """
        正しいリフレッシュトークンでアクセストークンを再発行できることをテスト
        """
        # ログインしてリフレッシュトークンを取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_logout_success(self):
        """
        正常にログアウトできることをテスト
        """
        # ログインしてトークンを取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get("access_token").value
        self.client.cookies["refresh_token"] = login_response.cookies.get("refresh_token").value

        # ログアウト
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")

        # Cookieが削除されていることを確認
        self.assertEqual(response.cookies.get("access_token").value, "")
        self.assertEqual(response.cookies.get("refresh_token").value, "")
