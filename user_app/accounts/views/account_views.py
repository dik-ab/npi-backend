import logging
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import pyotp
import qrcode
from io import BytesIO
import base64
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now, localtime

from user_app.accounts.serializer import AccountSerializer, TOTPVerifySerializer, PasswordResetSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer
from npi.utils import ERROR_MESSAGES
from shared.models import Account

# ロガーの設定
logger = logging.getLogger(__name__)


class MeView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        account = request.user
        if not account:
            logger.error("Unauthorized access attempt")
            return Response(
                ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def put(self, request):
        account = request.user
        if not account:
            logger.error("Unauthorized access attempt")
            return Response(
                ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error("Failed to update account: %s", serializer.errors)
        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


class AccountView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Failed to create account: %s", serializer.errors)
        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            sender_email = settings.DEFAULT_FROM_EMAIL
            email = serializer.validated_data['email']
            user = Account.objects.get(email=email)

            # トークン生成
            raw_token = serializer.create_reset_token(user)

            # メール送信
            reset_url = f"https://example.com/reset-password?token={raw_token}"
            try:
                send_mail(
                    subject="パスワード再設定",
                    message=f"以下のリンクからパスワードを再設定してください: {reset_url}",
                    from_email=sender_email,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response(
                    {
                        "status": "success",
                        "message": "パスワードリセットリンクを送信しました。"
                    }, status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": f"メールの送信に失敗しました: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetVerifyView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


class Generate2FAView(views.APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """QRコードとシークレットキーを生成"""
        user_totp = request.user

        if not user_totp.secret_key:
            user_totp.secret_key = pyotp.random_base32()
            user_totp.save()

        totp = pyotp.TOTP(user_totp.secret_key)
        provisioning_url = totp.provisioning_uri(
            request.user.email, issuer_name="NPIApp"
        )

        # QRコード生成
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # QRコードをバイナリに変換
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return Response(
            {
                "status": "success",
                "data": {
                    "qr_code": qr_code,
                    # include_keyがtrueの場合はシークレットキーを返す
                    "secret_key": (
                        user_totp.secret_key
                        if request.GET.get("include_key") == "true"
                        else None
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )


class Verify2FAView(views.APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)
    serializer_class = TOTPVerifySerializer

    def post(self, request):
        """2FAコードを検証"""
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_totp = request.user
        except Account.DoesNotExist:
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        verification_code = serializer.validated_data["code"]
        totp = pyotp.TOTP(user_totp.secret_key)

        if totp.verify(verification_code):
            # アカウントのlast_2fa_atを現在時刻で更新
            user_totp.last_2fa_at = localtime(now())
            user_totp.save()

            # 2要素認証完了フラグを追加してアクセストークンを再発行
            refresh = RefreshToken.for_user(user_totp)
            access = refresh.access_token

            access['isTwoFactorAuthenticated'] = True

            access_max_age = int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            )
            refresh_max_age = int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            )

            response = Response(
                {"status": "success", "message": "2FA検証が成功しました"}, status=status.HTTP_200_OK
            )
            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=settings.HTTPONLY_COOKIES,
                secure=settings.SECURE_COOKIES,
                samesite=None,
                max_age=access_max_age,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=settings.HTTPONLY_COOKIES,
                secure=settings.SECURE_COOKIES,
                samesite=None,
                max_age=refresh_max_age,
            )

            return response

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )
