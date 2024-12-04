from django.urls import reverse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APITestCase
from npi.utils import ERROR_MESSAGES
from django.contrib.auth.hashers import make_password
from accounts.models import Account
from announcements.models import Announcement


class AnnouncementListViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.url = reverse("announcement-list")
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

        # お知らせを作成
        now = make_aware(datetime.now())
        for i in range(15):
            Announcement.objects.create(
                title=f"Announcement {i}",
                content="Content",
                announcements_from_at=now,
                announcements_to_at=now + timedelta(days=1),
            )

    def test_get_announcements_success(self):
        """
        お知らせ一覧の取得
        """
        response = self.client.get(self.url, {"page": 1, "per_page": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 10)  # Default per_page is 10
        self.assertEqual(response.data["pagination"]["total_items"], 15)

    def test_get_announcements_unauthenticated(self):
        """
        お知らせ一覧の取得時に、未認証の場合
        """
        # 認証を無効にする
        self.client.cookies.clear()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, ERROR_MESSAGES["401_ERRORS"])

    def test_get_space_list_no_spaces(self):
        """
        お知らせ一覧の取得時に、お知らせが存在しない場合
        """
        Announcement.objects.all().delete()
        response = self.client.get(self.url, {"page": 1, "per_page": 10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, ERROR_MESSAGES["404_ERRORS"])

    def test_pagination(self):
        """
        お知らせ一覧の取得時に、ページネーションが正しく動作すること
        """
        response = self.client.get(self.url, {"page": 2, "per_page": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 5)
        self.assertEqual(response.data["pagination"]["current_page"], 2)
        self.assertEqual(response.data["pagination"]["per_page"], 5)
        self.assertEqual(response.data["pagination"]["total_pages"], 3)

    def test_get_announcements_outside_time_range(self):
        """
        お知らせ一覧の取得時に、現在時刻がannouncements_from_atとannouncements_to_atの範囲外のお知らせは取得できないこと
        """
        now = make_aware(datetime.now())
        Announcement.objects.create(
            title="Outside Announcement",
            content="Content",
            announcements_from_at=now + timedelta(days=1),
            announcements_to_at=now + timedelta(days=2),
        )
        response = self.client.get(self.url, {"page": 1, "per_page": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 10)  # Default per_page is 10
        self.assertNotIn(
            "Outside Announcement", [a["title"] for a in response.data["data"]]
        )
