from django.contrib.auth.hashers import check_password
from django.db import models
import uuid
from django.utils.timezone import now


class Account(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(null=False, blank=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    password = models.CharField(null=False, blank=False)
    secret_key = models.CharField(max_length=32, null=True, blank=True)
    last_2fa_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    reset_token = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="パスワードリセット用のトークン"
    )
    token_expiration = models.DateTimeField(
        blank=True,
        null=True,
        help_text="トークンの有効期限"
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.email

    def check_password(self, raw_password):
        """
        パスワードを検証
        """
        return check_password(raw_password, self.password)

    def is_reset_token_valid(self):
        """トークンが有効かをチェックする"""
        if self.reset_token and self.token_expiration:
            return self.token_expiration > now()
        return False


class Announcement(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="お知らせID")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    content = models.TextField(max_length=1000, verbose_name="内容")
    announcements_from_at = models.DateTimeField(verbose_name="お知らせ開始日時")
    announcements_to_at = models.DateTimeField(verbose_name="お知らせ終了日時")
    file_path = models.CharField(
        max_length=255, blank=True, verbose_name="ファイルパス"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    def __str__(self):
        return self.title


class Space(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="スペースID")
    name = models.CharField(
        null=False, blank=False, max_length=100, verbose_name="スペース名"
    )
    icon_image_path = models.CharField(
        max_length=500, null=False, blank=True, verbose_name="アイコン画像フルパス"
    )
    description = models.TextField(
        max_length=1000, null=False, blank=True, verbose_name="スペースの説明"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        db_table = "spaces"


class SpaceAccount(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="スペースアカウントID")
    space = models.ForeignKey(
        Space, on_delete=models.CASCADE, verbose_name="スペースID"
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, verbose_name="アカウントID"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        db_table = "space_accounts"


class Permission(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="権限ID")
    name = models.CharField(
        null=False, blank=False, max_length=100, verbose_name="権限名"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        db_table = "permissions"


class SpaceAccountPermission(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="スペースアカウント権限ID")
    space_account = models.ForeignKey(
        SpaceAccount, on_delete=models.CASCADE, verbose_name="スペースアカウントID"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, verbose_name="権限ID"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        db_table = "space_accounts_permissions"


class Project(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="プロジェクトID")
    logical_project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="論理プロジェクトID")
    name = models.CharField(null=False, blank=False, max_length=100, verbose_name="プロジェクト名", help_text="全角100文字以内")
    description = models.TextField(null=False, blank=True, verbose_name="プロジェクトの説明", help_text="全角1000文字以内")
    last_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="最終更新日時")
    space = models.ForeignKey(Space, on_delete=models.CASCADE, verbose_name="スペースID")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    def __str__(self):
        return self.name
