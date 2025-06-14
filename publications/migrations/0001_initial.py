# Generated by Django 5.2.1 on 2025-05-23 13:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="название")),
                ("body", models.TextField(verbose_name="содержание")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="publications/",
                        verbose_name="изображение",
                    ),
                ),
                (
                    "views_count",
                    models.IntegerField(verbose_name="количество просмотров"),
                ),
                ("likes_count", models.IntegerField(verbose_name="количество лайков")),
                (
                    "is_free",
                    models.BooleanField(default=True, verbose_name="бесплатно?"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "публикация",
                "verbose_name_plural": "публикации",
            },
        ),
        migrations.CreateModel(
            name="Commentary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField(verbose_name="содержание")),
                ("likes_count", models.IntegerField(verbose_name="количество лайков")),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор",
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="publications.publication",
                        verbose_name="публикация",
                    ),
                ),
            ],
            options={
                "verbose_name": "комментарий",
                "verbose_name_plural": "комментарии",
            },
        ),
    ]
