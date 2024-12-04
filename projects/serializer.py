from rest_framework import serializers
from django.core.validators import (
    MaxLengthValidator,
)
from projects.models import Project
from spaces.models import Space


def validate_space_exists(value):
    # 存在チェック ※論理削除されていないもののみチェック
    if not Space.objects.filter(id=value, deleted_at__isnull=True).exists():
        raise serializers.ValidationError("存在しないスペースが指定されています。")


class ProjectSerializer(serializers.ModelSerializer):
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

    space = serializers.IntegerField(
        required=True,
        validators=[
            validate_space_exists
        ],
        write_only=True,
    )

    def validate(self, data):
        if Project.objects.filter(name=data['name'], space=data['space']).exists():
            raise serializers.ValidationError("同じ名前とスペースの組み合わせが既に存在します。")
        return data

    class Meta:
        model = Project
        fields = [
            'id',
            'logical_project_id',
            'name',
            'description',
            'space',
            'last_updated_at',
        ]
        read_only_fields = ['id', 'logical_project_id']

    def to_representation(self, instance):
        # 通常のデータ表現を取得
        data = super().to_representation(instance)

        # 仮置き()
        data['last_status'] = "public"
        data['project_play_count_last_month'] = 12345
        data['projects_play_count_two_months_ago'] = 67890

        return data
