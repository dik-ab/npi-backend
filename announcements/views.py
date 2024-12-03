import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Announcement
from .serializers import AnnouncementSerializer
from npi.utils import ERROR_MESSAGES, CustomPagination

# ロガーの設定
logger = logging.getLogger(__name__)

# Create your views here.


class AnnouncementListView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # お知らせを取得
        announcements = Announcement.objects.filter(deleted_at__isnull=True)

        # ページネーションの設定
        paginator = CustomPagination()
        paginator.page_size = request.GET.get("per_page", 10)

        if not announcements.exists():
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        # ページネーションを適用
        page = paginator.paginate_queryset(announcements, request)
        if page is not None:
            serializer = AnnouncementSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )
