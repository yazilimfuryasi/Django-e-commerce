# Generated by Django 4.2.3 on 2023-07-24 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("index", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(
                allow_unicode=True, blank=True, db_index=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(
                allow_unicode=True, blank=True, db_index=False, null=True
            ),
        ),
    ]
