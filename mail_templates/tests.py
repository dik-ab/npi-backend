# tests.py

from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

class SendMailViewTests(APITestCase):
    def setUp(self):
        # テスト用のAPIエンドポイントURLを設定
        self.url = reverse('send-mail')
        self.valid_payload = {
            "recipient_email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message."
        }
        self.invalid_payload = {
            "recipient_email": "invalid-email",
            "subject": "Test Subject",
            "message": "This is a test message."
        }

    def test_send_mail_success(self):
        """メール送信が正常に行われることを確認する"""
        response = self.client.post(self.url, data=self.valid_payload, format='json')

        # ステータスコードが200であることを確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), "メールが正常に送信されました。")

        # メールが1通送信されていることを確認
        self.assertEqual(len(mail.outbox), 1)

        # メールの内容を確認
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, self.valid_payload["subject"])
        self.assertEqual(sent_mail.body, self.valid_payload["message"])
        self.assertEqual(sent_mail.to, [self.valid_payload["recipient_email"]])

    def test_send_mail_invalid_email(self):
        """無効なメールアドレスの場合、400エラーが返されることを確認する"""
        response = self.client.post(self.url, data=self.invalid_payload, format='json')

        # ステータスコードが400であることを確認
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # メールが送信されていないことを確認
        self.assertEqual(len(mail.outbox), 0)
