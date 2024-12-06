from rest_framework import serializers
from django.core.validators import (
    MaxLengthValidator,
)
from shared.models import Project
from user_app.contents.models import Contents, ProductionStatusEnum


def validate_project_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not Project.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError("存在しないプロジェクトが指定されています。")


class ContentsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(100, message="名前は100文字以下である必要があります。"),
        ],
    )

    description = serializers.CharField(
        validators=[
            MaxLengthValidator(1000, message="説明は1000文字以下である必要があります。"),
        ],
    )

    project = serializers.IntegerField(
        required=True,
        validators=[
            validate_project_exists
        ],
        write_only=True,
    )

    script_path = serializers.CharField(
        required=False,
    )

    is_10_return_move_on_display = serializers.BooleanField(
        required=False,
    )

    def validate(self, data):
        if Contents.objects.filter(name=data['name'], project=data['project']).exists():
            raise serializers.ValidationError("同じ名前のコンテンツが既に存在します。")
        return data

    class Meta:
        model = Contents
        fields = [
            'id',
            'logical_contents_id',
            'name',
            'description',
            'project',
            'last_updated_at',
            'script_path',
            'is_10_return_move_on_display',
        ]
        read_only_fields = ['id', 'logical_contents_id']

    def to_representation(self, instance):
        # 通常のデータ表現を取得
        data = super().to_representation(instance)

        # production_status_idをENUM名に変換
        try:
            data['production_status'] = ProductionStatusEnum(instance.production_status_id).name
        except ValueError:
            data['production_status'] = None
        return data