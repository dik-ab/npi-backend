from django.db import models
import uuid


class Project(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="プロジェクトID")
    logical_project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="論理プロジェクトID")
    name = models.CharField(null=False, blank=False, max_length=100, verbose_name="プロジェクト名", help_text="全角100文字以内")
    description = models.TextField(null=False, blank=True, verbose_name="プロジェクトの説明", help_text="全角1000文字以内")
    last_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="最終更新日時")
    space = models.ForeignKey('spaces.Space', on_delete=models.CASCADE, verbose_name="スペースID")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    def __str__(self):
        return self.name
