from django.db import models

class Announcement(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="お知らせID")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容", max_length=1000)
    announcements_from_at = models.DateTimeField(verbose_name="お知らせ開始日時")
    announcements_to_at = models.DateTimeField(verbose_name="お知らせ終了日時")
    file_path = models.CharField(max_length=255, blank=True, verbose_name="ファイルパス")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    def __str__(self):
        return self.title
