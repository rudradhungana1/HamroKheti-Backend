# Generated by Django 5.0.2 on 2024-03-20 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_remove_user_phone_farmerprofile_phone_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("inactive", "Inactive"),
                    ("locked", "Locked"),
                ],
                default="active",
            ),
        ),
    ]
