# Generated by Django 5.0.2 on 2024-04-18 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_order_completed"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="checkout_type",
            field=models.CharField(
                choices=[("cash", "Cash"), ("wallet", "Wallet")],
                default="cash",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="transaction_uuid",
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
