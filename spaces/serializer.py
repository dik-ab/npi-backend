from rest_framework import serializers
from django.core.validators import (
    MaxLengthValidator,
)
from .models import Space, SpaceAccount, Permission, SpaceAccountPermission
from accounts.serializer import AccountSerializer
from accounts.models import Account


class SpaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(100, message="名前は100文字以下である必要があります。"),
        ],
    )

    icon_image_path = serializers.CharField(
        validators=[
            MaxLengthValidator(
                500, message="アイコン画像フルパスは500文字以下である必要があります。"
            ),
        ],
    )

    description = serializers.CharField(
        validators=[
            MaxLengthValidator(
                1000, message="説明は1000文字以下である必要があります。"
            ),
        ],
    )

    class Meta:
        model = Space
        fields = [
            "id",
            "name",
            "icon_image_path",
            "description",
        ]  # 'deleted_at'を除外


def validate_space_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not Space.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError("存在しないスペースが指定されています。")


def validate_account_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not Account.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError("存在しないアカウントが指定されています。")


class SpaceAccountCreateSerializer(serializers.ModelSerializer):

    space = serializers.IntegerField(required=True, validators=[validate_space_exists])
    account = serializers.IntegerField(
        required=True, validators=[validate_account_exists]
    )

    def validate(self, data):
        space_id = (
            data.get("space").id
            if isinstance(data.get("space"), Space)
            else data.get("space")
        )
        account_id = (
            data.get("account").id
            if isinstance(data.get("account"), Account)
            else data.get("account")
        )

        # 重複チェック
        existing_instance = SpaceAccount.objects.filter(
            space_id=space_id,
            account_id=account_id,
            # 論理削除されていないもののみチェック
            deleted_at__isnull=True,
        ).first()

        if existing_instance:
            raise serializers.ValidationError(
                "指定されたスペースとアカウントの組み合わせは既に存在します。"
            )

        return data

    class Meta:
        model = SpaceAccount
        fields = [
            "id",
            "space",
            "account",
        ]  # 'deleted_at'を除外


class SpaceAccountSerializer(serializers.ModelSerializer):
    space = SpaceSerializer(read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = SpaceAccount
        fields = ["id", "space", "account"]


class PermissionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(100, message="名前は100文字以下である必要があります。"),
        ],
    )

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
        ]  # 'deleted_at'を除外


def validate_space_account_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not SpaceAccount.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError(
            "存在しないスペース-アカウントが指定されています。"
        )


def validate_permission_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not Permission.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError("存在しない権限が指定されています。")


class SpaceAccountPermissionCreateSerializer(serializers.ModelSerializer):

    space_account = serializers.IntegerField(
        required=True, validators=[validate_space_account_exists]
    )
    permission = serializers.IntegerField(
        required=True, validators=[validate_permission_exists]
    )

    def validate(self, data):
        space_account_id = (
            data.get("space_account").id
            if isinstance(data.get("space_account"), SpaceAccount)
            else data.get("space_account")
        )
        permission_id = (
            data.get("permission").id
            if isinstance(data.get("permission"), Permission)
            else data.get("permission")
        )

        # 重複チェック
        existing_instance = SpaceAccountPermission.objects.filter(
            space_account_id=space_account_id,
            permission_id=permission_id,
            # 論理削除されていないもののみチェック
            deleted_at__isnull=True,
        ).first()

        if existing_instance:
            raise serializers.ValidationError(
                "指定されたスペース-アカウントと権限の組み合わせは既に存在します。"
            )

        return data

    class Meta:
        model = SpaceAccountPermission
        fields = [
            "id",
            "space_account",
            "permission",
        ]  # 'deleted_at'を除外


class SpaceAccountPermissionSerializer(serializers.ModelSerializer):
    space_account = SpaceAccountSerializer(read_only=True)
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = SpaceAccountPermission
        fields = ["id", "space_account", "permission"]
