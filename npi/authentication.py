from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import Account
import logging
from npi.utils import ERROR_MESSAGES

# ロガーの設定
logger = logging.getLogger(__name__)

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # クッキーからトークンを取得
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            logger.error("No access token found in cookies")
            raise AuthenticationFailed(ERROR_MESSAGES["401_ERRORS"])

        try:
            logger.debug("Access Token: %s", access_token)
            # トークンを検証
            validated_token = AccessToken(access_token)
            logger.debug("Decoded Token: %s", validated_token.payload)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Account.DoesNotExist:
            logger.error("User not found for token: %s", validated_token.payload)
            raise AuthenticationFailed(ERROR_MESSAGES["404_ERRORS"])
        except Exception as e:
            logger.error("Token validation failed: %s", str(e))
            raise AuthenticationFailed(ERROR_MESSAGES["403_ERRORS"])

    def get_user(self, validated_token):
        user_id = validated_token["user_id"]
        return Account.objects.get(id=user_id)
