# Generated by Django 4.2.16 on 2024-12-02 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="権限ID"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="権限名")),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="削除日時"
                    ),
                ),
            ],
            options={
                "db_table": "permissions",
            },
        ),
        migrations.CreateModel(
            name="Space",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="スペースID"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="スペース名")),
                (
                    "icon_image_path",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="アイコン画像フルパス"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, max_length=1000, verbose_name="スペースの説明"
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="削除日時"
                    ),
                ),
            ],
            options={
                "db_table": "spaces",
            },
        ),
        migrations.CreateModel(
            name="SpaceAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        verbose_name="スペースアカウントID",
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="削除日時"
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.account",
                        verbose_name="アカウントID",
                    ),
                ),
                (
                    "space",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spaces.space",
                        verbose_name="スペースID",
                    ),
                ),
            ],
            options={
                "db_table": "space_accounts",
            },
        ),
        migrations.CreateModel(
            name="SpaceAccountPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        verbose_name="スペースアカウント権限ID",
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="削除日時"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spaces.permission",
                        verbose_name="権限ID",
                    ),
                ),
                (
                    "space_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spaces.spaceaccount",
                        verbose_name="スペースアカウントID",
                    ),
                ),
            ],
            options={
                "db_table": "space_accounts_permissions",
            },
        ),
    ]