import logging
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import pyotp
import qrcode
from io import BytesIO
import base64

from ..serializer import AccountSerializer, TOTPVerifySerializer
from npi.utils import ERROR_MESSAGES
from ..models import Account

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
            request.user.email,
            issuer_name='NPIApp'
        )

        # QRコード生成
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # QRコードをバイナリに変換
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'status': 'success',
            'data': {
                'qr_code': qr_code,
                # include_keyがtrueの場合はシークレットキーを返す
                'secret_key': user_totp.secret_key if request.GET.get('include_key') == 'true' else None
            }
        }, status=status.HTTP_200_OK)


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

        verification_code = serializer.validated_data['code']
        totp = pyotp.TOTP(user_totp.secret_key)

        if totp.verify(verification_code):
            return Response({
                'status': 'success',
                'message': '2FA検証が成功しました'
            }, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )
