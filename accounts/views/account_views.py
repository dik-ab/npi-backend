import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..serializer import AccountSerializer
from npi.utils import ERROR_MESSAGES

# ロガーの設定
logger = logging.getLogger(__name__)


class MeView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        account = request.user
        if not account:
            logger.error("Unauthorized access attempt")
            return Response(ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def put(self, request):
        account = request.user
        if not account:
            logger.error("Unauthorized access attempt")
            return Response(ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error("Failed to update account: %s", serializer.errors)
        return Response(ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    # 認証クラスを無効にする
    authentication_classes = []

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Failed to create account: %s", serializer.errors)
        return Response(ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST)
