from django.db import models


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
        "accounts.Account", on_delete=models.CASCADE, verbose_name="アカウントID"
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
