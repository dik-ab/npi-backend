# tests.py

from django.core import mail
from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shared.models import Account
from django.contrib.auth.hashers import make_password


class SendMailViewTests(APITestCase):
    def setUp(self):
        # テスト用のAPIエンドポイントURLを設定
        self.url = reverse("send-mail", host='user_app')
        self.valid_payload = {
            "recipient_email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message.",
        }
        self.invalid_payload = {
            "recipient_email": "invalid-email",
            "subject": "Test Subject",
            "message": "This is a test message.",
        }

        self.login_url = reverse("login", host='user_app')
        # テスト用ユーザーを作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),  # パスワードを暗号化して保存
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

    def test_send_mail_success(self):
        """メール送信が正常に行われることを確認する"""
        response = self.client.post(self.url, data=self.valid_payload, format="json")

        # ステータスコードが200であることを確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("message"), "メールが正常に送信されました。"
        )

        # メールが1通送信されていることを確認
        self.assertEqual(len(mail.outbox), 1)

        # メールの内容を確認
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, self.valid_payload["subject"])
        self.assertEqual(sent_mail.body, self.valid_payload["message"])
        self.assertEqual(sent_mail.to, [self.valid_payload["recipient_email"]])

    def test_send_mail_invalid_email(self):
        """無効なメールアドレスの場合、400エラーが返されることを確認する"""
        response = self.client.post(self.url, data=self.invalid_payload, format="json")

        # ステータスコードが400であることを確認
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # メールが送信されていないことを確認
        self.assertEqual(len(mail.outbox), 0)
