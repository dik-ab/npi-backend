from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import Account
import logging
from datetime import datetime, timezone
from npi.utils import ERROR_MESSAGES

# ロガーの設定
logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # クッキーからトークンを取得
        access_token = request.COOKIES.get('access_token')
        # クッキーにアクセストークンがない場合
        if not access_token:
            logger.error("No access token found in cookies")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

        try:
            # トークンを検証
            validated_token = AccessToken(access_token)

            # 無効な場合
            if not validated_token:
                logger.error("Invalid token")
                raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

            # 期限切れの場合
            if datetime.fromtimestamp(validated_token["exp"], timezone.utc) < datetime.now(timezone.utc):
                logger.error("Token is expired")
                raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception:
            logger.error("Token validation failed")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

    def get_user(self, validated_token):
        user_id = validated_token["user_id"]
        return Account.objects.get(id=user_id)
