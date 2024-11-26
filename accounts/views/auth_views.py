import logging
from django.utils.timezone import now
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from npi.utils import ERROR_MESSAGES
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account

# ロガーの設定
logger = logging.getLogger(__name__)


class LoginView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # 必須フィールドのチェック
        if not email or not password:
            logger.error("Email or password not provided")
            return Response(
                ERROR_MESSAGES["400_ERRORS"],
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ユーザー認証
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            logger.error(f"User with email {email} does not exist")
            return Response(
                ERROR_MESSAGES["401_ERRORS"],
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user or user.deleted_at is not None or not user.check_password(password):
            # 存在しないユーザー or 削除済みユーザー or パスワードが間違っている場合に同じエラーメッセージを返す
            logger.error(f"Invalid password for user with email {email}")
            return Response(
                ERROR_MESSAGES["401_ERRORS"],
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # JWTトークンの生成
        try:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            access_max_age = int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            )
            refresh_max_age = int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            )

            # アカウントのlast_login_atを現在時刻で更新
            user.last_login_at = now()
            user.save()

            # HttpOnly Cookie にトークンを設定
            response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=settings.HTTPONLY_COOKIES,
                secure=settings.SECURE_COOKIES,
                samesite=None,
                # 有効期限（秒）
                max_age=access_max_age,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=settings.HTTPONLY_COOKIES,
                secure=settings.SECURE_COOKIES,
                samesite=None,
                # 有効期限（秒）
                max_age=refresh_max_age,
            )
            return response
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return Response(
                ERROR_MESSAGES["500_ERRORS"],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefreshTokenView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        # Cookieからリフレッシュトークンを取得
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            logger.error("Refresh token not provided in cookies")
            return Response(
                ERROR_MESSAGES["400_ERRORS"],
                status=status.HTTP_400_BAD_REQUEST,
            )
        # リフレッシュトークンで新しいアクセストークンを生成
        try:
            request.data["refresh"] = refresh_token
            response = super().post(request, *args, **kwargs)
            access_token = response.data.get("access")

            response.set_cookie(
                key="access_token",
                value=str(access_token),
                httponly=settings.HTTPONLY_COOKIES,
                secure=settings.SECURE_COOKIES,
                samesite=None,
                max_age=15 * 60,  # 有効期限
            )
            return response
        except InvalidToken:
            logger.error("Invalid refresh token provided")
            return Response(
                ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError as e:
            logger.error(f"Token error: {str(e)}")
            return Response(
                {"detail": "Refresh token has expired or is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
