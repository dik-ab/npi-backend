import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializer import SpaceAccountSerializer
from npi.utils import ERROR_MESSAGES, CustomPagination
from .models import SpaceAccount

# ロガーの設定
logger = logging.getLogger(__name__)


class SpaceListView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # ユーザーが所属しているスペースを取得
        space_accounts = SpaceAccount.objects.filter(account=request.user, deleted_at__isnull=True)

        # 必須チェック
        if request.GET.get("page") is None:
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )
        if request.GET.get("per_page") is None:
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        # ページネーションの設定
        paginator = CustomPagination()
        paginator.page_size = request.GET.get("per_page", 10)

        if not space_accounts.exists():
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        # ページネーションを適用
        page = paginator.paginate_queryset(space_accounts, request)
        if page is not None:
            serializer = SpaceAccountSerializer(page, many=True)
            filtered_data = [
                item["space"] for item in serializer.data
            ]
            return paginator.get_paginated_response(filtered_data)

        serializer = SpaceAccountSerializer(space_accounts, many=True)
        filtered_data = [
            item["space"] for item in serializer.data
        ]

        return Response({
            'status': 'success',
            'data': filtered_data
        }, status=status.HTTP_200_OK)
