# Generated by Django 5.0.2 on 2024-03-04 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
