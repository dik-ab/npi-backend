# Generated by Django 4.2.16 on 2024-12-06 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_delete_project"),
        ("spaces", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="spaceaccount",
            name="account",
        ),
        migrations.RemoveField(
            model_name="spaceaccount",
            name="space",
        ),
        migrations.RemoveField(
            model_name="spaceaccountpermission",
            name="permission",
        ),
        migrations.RemoveField(
            model_name="spaceaccountpermission",
            name="space_account",
        ),
        migrations.DeleteModel(
            name="Permission",
        ),
        migrations.DeleteModel(
            name="Space",
        ),
        migrations.DeleteModel(
            name="SpaceAccount",
        ),
        migrations.DeleteModel(
            name="SpaceAccountPermission",
        ),
    ]
