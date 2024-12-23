from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from shared.models import Account
import logging
from npi.utils import ERROR_MESSAGES

# ロガーの設定
logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # クッキーからアクセストークンを取得
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            logger.error("Access token not found in cookies")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

        try:
            # トークン検証
            validated_token = AccessToken(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        # トークン検証で例外が発生した場合（トークンの有効期限切れなど）
        except Exception:
            logger.error("An error occurred during access token validation.")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

    def get_user(self, validated_token):
        """トークンのユーザーを取得"""
        user_id = validated_token.get("user_id")
        if not user_id:
            logger.error("Token does not contain user_id")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])
        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])
        return user
