# Generated by Django 4.2.3 on 2023-08-05 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("index", "0007_remove_shippingfee_free_shipping_fee"),
    ]

    operations = [
        migrations.RemoveField(model_name="shippingfee", name="limit_amount",),
        migrations.AddField(
            model_name="shippingfee",
            name="limit",
            field=models.DecimalField(
                decimal_places=2,
                default=300,
                max_digits=10,
                verbose_name="Ücretsiz Kargo Limiti",
            ),
        ),
    ]
