# Generated by Django 4.2.16 on 2024-12-03 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("announcements", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="announcement",
            name="content",
            field=models.TextField(max_length=1000, verbose_name="内容"),
        ),
    ]
