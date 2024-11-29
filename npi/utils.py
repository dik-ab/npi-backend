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
