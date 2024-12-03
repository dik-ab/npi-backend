from rest_framework import status
from rest_framework.test import APITestCase
from npi.utils import ERROR_MESSAGES
from django.urls import reverse
from spaces.models import Space, SpaceAccount
from accounts.models import Account
from django.contrib.auth.hashers import make_password
import logging

# ロガーの設定
logger = logging.getLogger(__name__)


class SpaceListViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.url = reverse('spaces-list')
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

        self.space1 = Space.objects.create(name='Test Space 1', icon_image_path='path/to/icon1.png', description='This is a test space description.')
        self.space2 = Space.objects.create(name='Test Space 2', icon_image_path='path/to/icon2.png', description='This is a test space description.')
        self.space3 = Space.objects.create(name='Test Space 3', icon_image_path='path/to/icon3.png', description='This is a test space description.')
        SpaceAccount.objects.create(space=self.space1, account=self.account1)
        SpaceAccount.objects.create(space=self.space2, account=self.account1)
        SpaceAccount.objects.create(space=self.space3, account=self.account1)

    def test_get_space_list_success(self):
        """
        スペース一覧の取得
        """
        response = self.client.get(self.url, {'page': 1, 'per_page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 2)

    def test_get_space_list_no_spaces(self):
        """
        スペースが存在しない場合のスペース一覧を取得
        """
        SpaceAccount.objects.all().delete()
        response = self.client.get(self.url, {'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, ERROR_MESSAGES["404_ERRORS"])

    def test_get_space_list_unauthenticated(self):
        """
        認証されていないスペース一覧を取得しようとする
        """
        # 認証を無効にする
        self.client.cookies.clear()
        response = self.client.get(self.url, {'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_response = ERROR_MESSAGES["401_ERRORS"]
        self.assertEqual(response.data, expected_response)
