import logging
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..serializer import AccountSerializer
from npi.utils import ERROR_MESSAGES

# ロガーの設定
logger = logging.getLogger(__name__)

class MeView(APIView):
    permission_classes = (IsAuthenticated,) # 認証が必要

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
    
    def delete(self, request):
        account = request.user
        password = request.data.get("password")

        if not password:
            logger.error("Password not provided for account deletion")
            return Response(ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST)

        if not account.check_password(password):
            logger.error("Invalid password provided for account deletion")
            return Response(ERROR_MESSAGES["401_ERRORS"], status=status.HTTP_401_UNAUTHORIZED)

        account.deleted_at = now()
        account.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountView(APIView):
    authentication_classes = [] # 認証クラスを無効にする

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Failed to create account: %s", serializer.errors)
        return Response(ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST)
