from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from accounts.models import Account
from npi.settings.base import SIMPLE_JWT

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # ユーザー認証
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user or not user.check_password(password):
            # 存在しないユーザーでも、パスワードが間違っている場合でも同じエラーメッセージを返す
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        # JWTトークンの生成
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        access_max_age = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        refresh_max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

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
            return Response({"error": "Refresh token is missing"}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response