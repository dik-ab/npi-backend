from rest_framework import status
from rest_framework.test import APITestCase
from npi.utils import ERROR_MESSAGES
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from accounts.models import Account
import logging
import pyotp

# ロガーの設定
logger = logging.getLogger(__name__)


class MeViewTestCase(APITestCase):

    def setUp(self):
        self.login_url = reverse("login")
        self.me_url = reverse("me")

        # テスト用ユーザーを作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            # パスワードを暗号化して保存
            password=make_password("securepassword1"),
            name="Test User",
        )
        self.account1.save()

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_get_me_success(self):
        """
        自身のアカウント情報取得成功
        """
        response = self.client.get(self.me_url)
        logger.info(f"Request Cookies: {self.client.cookies}")
        logger.info(f"Response Cookies: {response.cookies}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = {
            "id": self.account1.id,
            "name": self.account1.name,
            "email": self.account1.email,
        }
        for key in expected_response:
            self.assertEqual(response.data[key], expected_response[key])

    def test_get_me_unauthorized(self):
        """
        認証されていない状態で自身のアカウント情報を取得しようとする
        """
        # 認証を無効にする
        self.client.cookies.clear()
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_update_me_success(self):
        """
        自身のアカウント情報を正常に更新
        """
        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

        update_data = {
            "name": "Updated Name",
        }
        response = self.client.put(self.me_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.name, update_data["name"])
        expected_response = {
            "id": self.account1.id,
            "name": self.account1.name,
            "email": self.account1.email,
        }
        for key in expected_response:
            self.assertEqual(response.data[key], expected_response[key])

    def test_update_me_invalid_data(self):
        """
        無効なデータで自身のアカウント情報を更新
        """
        update_data = {
            "email": "invalid-email",
        }
        response = self.client.put(self.me_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = ERROR_MESSAGES["400_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_update_me_unauthorized(self):
        """
        認証されていない状態で自身のアカウント情報を更新しようとする
        """
        # 認証を無効にする
        self.client.cookies.clear()
        update_data = {
            "name": "Updated Name",
        }
        response = self.client.put(self.me_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)


class AccountViewTestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.account_url = reverse("account_create")

        self.valid_account_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepassword3",
        }

    def test_post_single_account_success(self):
        """
        アカウント作成成功
        """
        response = self.client.post(self.account_url, data=self.valid_account_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.valid_account_data["email"])
        self.assertTrue(
            Account.objects.filter(email=self.valid_account_data["email"]).exists()
        )
        created_account = Account.objects.get(email=self.valid_account_data["email"])
        expected_response = {
            "id": created_account.id,
            "name": created_account.name,
            "email": created_account.email,
        }
        for key in expected_response:
            self.assertEqual(response.data[key], expected_response[key])

    def test_post_single_account_invalid_input(self):
        """
        無効なデータでアカウントを作成
        """
        invalid_data = {
            "name": "Invalid User",
            # 空のメールアドレス
            "email": "",
            "password": "securepassword4",
        }
        response = self.client.post(self.account_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class Generate2FAViewTestCase(APITestCase):

    def setUp(self):
        self.login_url = reverse("login")
        self.generate_2fa_url = reverse("2fa-generate")

        # テスト用ユーザーを作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),
            name="Test User",
        )
        self.account1.save()

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_generate_2fa_success(self):
        """
        2FAのQRコードとシークレットキーの生成成功
        """
        response = self.client.get(self.generate_2fa_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("qr_code", response.data["data"])
        self.assertIsNotNone(response.data["data"]["qr_code"])

    def test_generate_2fa_include_key(self):
        """
        include_keyがtrueの場合、シークレットキーを含む
        """
        response = self.client.get(self.generate_2fa_url, {"include_key": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("qr_code", response.data["data"])
        self.assertIn("secret_key", response.data["data"])
        self.assertIsNotNone(response.data["data"]["qr_code"])
        self.assertIsNotNone(response.data["data"]["secret_key"])

    def test_generate_2fa_unauthorized(self):
        """
        認証されていない状態で2FAのQRコードとシークレットキーを生成しようとする
        """
        # 認証を無効にする
        self.client.cookies.clear()
        response = self.client.get(self.generate_2fa_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)


class Verify2FAViewTestCase(APITestCase):

    def setUp(self):
        self.login_url = reverse("login")
        self.verify_2fa_url = reverse("2fa-verify")

        # テスト用ユーザーを作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),
            name="Test User",
            secret_key=pyotp.random_base32(),
        )
        self.account1.save()

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_verify_2fa_success(self):
        """
        2FAコードの検証成功
        """
        totp = pyotp.TOTP(self.account1.secret_key)
        valid_code = totp.now()
        response = self.client.post(self.verify_2fa_url, data={"code": valid_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "2FA検証が成功しました")
        self.account1.refresh_from_db()

    def test_verify_2fa_invalid_code(self):
        """
        無効な2FAコードの検証
        """
        invalid_code = "123456"
        response = self.client.post(self.verify_2fa_url, data={"code": invalid_code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = ERROR_MESSAGES["400_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_verify_2fa_missing_code(self):
        """
        2FAコードが提供されていない場合の検証
        """
        response = self.client.post(self.verify_2fa_url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = ERROR_MESSAGES["400_ERRORS"]
        self.assertEqual(response.data, expected_response)

    def test_verify_2fa_unauthorized(self):
        """
        認証されていない状態で2FAコードを検証しようとする
        """
        # 認証を無効にする
        self.client.cookies.clear()
        totp = pyotp.TOTP(self.account1.secret_key)
        valid_code = totp.now()
        response = self.client.post(self.verify_2fa_url, data={"code": valid_code})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)
