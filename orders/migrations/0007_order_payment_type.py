# Generated by Django 5.0.2 on 2024-04-28 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0006_order_checkout_type_order_transaction_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_type",
            field=models.CharField(
                choices=[("pending", "Pending"), ("complete", "Complete")],
                default="pending",
                max_length=100,
            ),
        ),
    ]
