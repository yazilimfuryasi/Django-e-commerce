# Generated by Django 4.2.3 on 2023-08-05 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("index", "0004_product_campaign"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="discounted_price",
            field=models.FloatField(blank=True, null=True),
        ),
    ]