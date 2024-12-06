from django.db import models
import uuid
from enum import Enum


class ProductionStatusEnum(Enum):
    UNDER_CONSTRUCTION = 1
    COMPLETION = 2


class Contents(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="コンテンツID")

    def generate_random_id():
        return uuid.uuid4().hex[:6]

    logical_contents_id = models.CharField(
        max_length=6,
        unique=True,
        default=generate_random_id,
        verbose_name="論理コンテンツID"
    )

    name = models.CharField(null=False, blank=False, max_length=100, verbose_name="コンテンツ名")
    description = models.TextField(null=False, blank=True, verbose_name="コンテンツの説明")
    project = models.ForeignKey('shared.Project', on_delete=models.CASCADE, verbose_name="プロジェクトID")
    production_status_id = models.IntegerField(
        choices=[(tag.value, tag.name) for tag in ProductionStatusEnum],
        default=ProductionStatusEnum.UNDER_CONSTRUCTION.value,
        verbose_name="製作ステータスID"
    )
    last_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="最終更新日時")
    script_path = models.CharField(max_length=1000, blank=True, verbose_name="スクリプトファイルパス")
    is_10_return_move_on_display = models.BooleanField(default=False, verbose_name="10秒戻る/進む")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        verbose_name = "コンテンツ"
        verbose_name_plural = "コンテンツ"
