# Generated by Django 5.0.2 on 2024-03-08 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_remove_user_is_admin_remove_user_is_farmer_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="user_role",
            field=models.CharField(
                choices=[
                    ("normal_user", "Normal User"),
                    ("admin", "Admin"),
                    ("farmer", "Farmer"),
                    ("partner", "Partner"),
                ],
                default="normal_user",
                max_length=20,
            ),
        ),
    ]
