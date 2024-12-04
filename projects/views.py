import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from npi.utils import ERROR_MESSAGES, CustomPagination, check_space_permission
from projects.models import Project
from spaces.models import Space, Permission
from projects.serializer import ProjectSerializer
from django.utils import timezone

# ロガーの設定
logger = logging.getLogger(__name__)


# 一覧/作成用
class ProjectListCreateAPIView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    # 一覧取得
    def get(self, request, space_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['space_admin', 'creator', 'disrtibutor', 'viewer']
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

        projects = Project.objects.filter(space_id=space_id, deleted_at__isnull=True)
        # ページネーションを適用
        page = paginator.paginate_queryset(projects, request)
        if page is not None:
            serializer = ProjectSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProjectSerializer(projects, many=True)

        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # 作成
    def post(self, request, space_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['space_admin']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['space'] = space_id
        data['last_updated_at'] = timezone.now()
        serializer = ProjectSerializer(data=data)

        if serializer.is_valid():
            space = Space.objects.get(id=space_id, deleted_at__isnull=True)
            # validated_dataを上書き
            serializer.save(
                space=space,
            )
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )


# 詳細/更新/削除用
class ProjectRetrieveUpdateDestroyAPIView(APIView):
    # 認証が必要
    permission_classes = (IsAuthenticated,)

    # 詳細取得
    def get(self, request, space_id, project_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['space_admin', 'creator', 'disrtibutor', 'viewer']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        project = Project.objects.get(id=project_id, space_id=space_id, deleted_at__isnull=True)

        if not project:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(project)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # 更新
    def put(self, request, space_id, project_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['space_admin']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        project = Project.objects.get(id=project_id, space_id=space_id, deleted_at__isnull=True)

        if not project:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data['space'] = space_id
        data['last_updated_at'] = timezone.now()
        serializer = ProjectSerializer(project, data)
        if serializer.is_valid():
            space = Space.objects.get(id=space_id, deleted_at__isnull=True)
            # validated_dataを上書き
            serializer.save(
                space=space,
            )
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response(
            ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
        )

    # 削除
    def delete(self, request, space_id, project_id):
        # ユーザーがそのスペースでの対象の操作権限があるかチェック
        permission_names = ['space_admin']
        permission_ids = list(Permission.objects.filter(name__in=permission_names, deleted_at__isnull=True).values_list('id', flat=True))
        if not check_space_permission(request.user, space_id, permission_ids):
            return Response(
                ERROR_MESSAGES["400_ERRORS"], status=status.HTTP_400_BAD_REQUEST
            )

        project = Project.objects.get(id=project_id, space_id=space_id, deleted_at__isnull=True)

        if not project:
            return Response(
                ERROR_MESSAGES["404_ERRORS"], status=status.HTTP_404_NOT_FOUND
            )

        project.delete()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
