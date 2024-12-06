import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from npi.utils import ERROR_MESSAGES, CustomPagination, check_space_permission
from shared.models import Project, Permission
from user_app.contents.models import Contents
from user_app.contents.serializer import ContentsSerializer
from django.utils import timezone

# ロガーの設定
logger = logging.getLogger(__name__)


# 一覧/作成用
class ContentsListCreateAPIView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    # 一覧取得
    def get(self, request, space_id, project_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))

        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

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

        contents = Contents.objects.filter(project_id=project_id, deleted_at__isnull=True)

        # production_statusで絞り込み
        production_status = request.GET.get("production_status")
        if production_status:
            contents = contents.filter(production_status_id=production_status)

        # ページネーションを適用
        page = paginator.paginate_queryset(contents, request)
        if page is not None:
            serializer = ContentsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ContentsSerializer(contents, many=True)

        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # 作成
    def post(self, request, space_id, project_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['project'] = project_id
        data['last_updated_at'] = timezone.now()
        serializer = ContentsSerializer(data=data)

        if serializer.is_valid():
            project = Project.objects.get(id=project_id, deleted_at__isnull=True)
            # validated_dataを上書き
            serializer.save(
                project=project,
            )
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


# 詳細/複製/更新/削除用
class ContentsRetrieveReproduceUpdateDestroyAPIView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    # 詳細取得
    def get(self, request, space_id, project_id, contents_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        contents = Contents.objects.get(id=contents_id, project_id=project_id, deleted_at__isnull=True)

        if not contents:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContentsSerializer(contents)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # 複製
    def post(self, request, space_id, project_id, contents_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        # 複製元のコンテンツを取得
        base_contents = Contents.objects.get(id=contents_id, project_id=project_id, deleted_at__isnull=True)

        if not base_contents:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        content_data = {
            'name': data['name'],
            'description': data['description'],
            'project': project_id,
            'production_status_id': base_contents.production_status_id,
            'script_path': base_contents.script_path,
            'is_10_return_move_on_display': base_contents.is_10_return_move_on_display,
            'last_updated_at': timezone.now(),
        }

        serializer = ContentsSerializer(data=content_data)

        if serializer.is_valid():
            project = Project.objects.get(id=project_id, deleted_at__isnull=True)
            # validated_dataを上書き
            serializer.save(
                project=project,
            )

            # 実際はその他の情報も複製するが、現時点ではコンテンツ情報のみ複製する
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )

    # 更新
    def put(self, request, space_id, project_id, contents_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        contents = Contents.objects.get(id=contents_id, project_id=project_id, deleted_at__isnull=True)

        if not contents:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data['project'] = project_id
        data['last_updated_at'] = timezone.now()
        serializer = ContentsSerializer(contents, data)

        if serializer.is_valid():
            project = Project.objects.get(id=project_id, deleted_at__isnull=True)
            # validated_dataを上書き
            serializer.save(
                project=project,
            )
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )

    # 削除
    def delete(self, request, space_id, project_id, contents_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['creator']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        contents = Contents.objects.get(id=contents_id, project_id=project_id, deleted_at__isnull=True)

        if not contents:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        contents.delete()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
