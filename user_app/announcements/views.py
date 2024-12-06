import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from shared.models import Announcement
from user_app.announcements.serializers import AnnouncementSerializer
from npi.utils import ERROR_MESSAGES, CustomPagination
from django.utils import timezone

# ロガーの設定
logger = logging.getLogger(__name__)

# Create your views here.


class AnnouncementListView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # 現在時刻を取得
        now = timezone.now()

        # 現在時刻がannouncements_from_at〜announcements_to_atの範囲に入っている、かつdeleted_atがnull（論理削除してない）のお知らせを、idが大きい順にソート
        announcements = Announcement.objects.all().filter(
            announcements_from_at__lte=now, announcements_to_at__gte=now, deleted_at__isnull=True
        ).order_by('-id')

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
