from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# エラーメッセージの定義
ERROR_MESSAGES = {
    "400_ERRORS": {
        "status": "error",
        "error": {"code": "INVALID_INPUT", "message": "入力が無効です"},
    },
    "401_ERRORS": {
        "status": "error",
        "error": {"code": "UNAUTHORIZED", "message": "認証に失敗しました"},
    },
    "403_ERRORS": {
        "status": "error",
        "error": {"code": "FORBIDDEN", "message": "アクセスが拒否されました"},
    },
    "404_ERRORS": {
        "status": "error",
        "error": {"code": "NOT_FOUND", "message": "リソースが見つかりません"},
    },
    "500_ERRORS": {
        "status": "error",
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "サーバーエラーが発生しました",
        },
    },
}


# 共通のページネーション付きレスポンス
class CustomPagination(PageNumberPagination):
    page_size_query_param = "per_page"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "data": data,
                "pagination": {
                    "current_page": self.page.number,
                    "per_page": self.page.paginator.per_page,
                    "total_pages": self.page.paginator.num_pages,
                    "total_items": self.page.paginator.count,
                },
            },
            status=status.HTTP_200_OK,
        )
