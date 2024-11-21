from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from npi.utils import ERROR_MESSAGES

from accounts.models import Account


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # 必須フィールドのチェック
        if not email or not password:
            return Response(
                ERROR_MESSAGES["400_ERRORS"],
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ユーザー認証
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response(
                ERROR_MESSAGES["404_ERRORS"],
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user or not user.check_password(password):
            # 存在しないユーザーでも、パスワードが間違っている場合でも同じエラーメッセージを返す
            return Response(
                ERROR_MESSAGES["401_ERRORS"],
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # JWTトークンの生成
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        access_max_age = int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        refresh_max_age = int(
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )

        print(settings.SECURE_COOKIES)
        # HttpOnly Cookie にトークンを設定
        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="Strict",
            max_age=access_max_age,  # 有効期限（秒）
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="Strict",
            max_age=refresh_max_age,  # 有効期限（秒）
        )
        return response


class RefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Cookieからリフレッシュトークンを取得
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
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
                httponly=True,
                secure=settings.SECURE_COOKIES,
                samesite="Strict",
                max_age=15 * 60,  # 有効期限
            )
            return response
        except InvalidToken:
            return Response(
                ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
