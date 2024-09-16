# Generated by Django 5.0.2 on 2024-03-20 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_partnerprofile_delivery_charge"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="phone",
        ),
        migrations.AddField(
            model_name="farmerprofile",
            name="phone",
            field=models.CharField(
                blank=True, default=None, max_length=10, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="partnerprofile",
            name="phone",
            field=models.CharField(
                blank=True, default=None, max_length=10, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="phone",
            field=models.CharField(
                blank=True, default=None, max_length=10, null=True, unique=True
            ),
        ),
    ]
