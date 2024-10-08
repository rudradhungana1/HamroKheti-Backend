# Generated by Django 5.0.2 on 2024-03-23 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0017_alter_partnerprofile_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="farmerprofile",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user_profile_percentage",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
