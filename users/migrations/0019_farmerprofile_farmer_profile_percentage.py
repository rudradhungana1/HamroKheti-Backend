# Generated by Django 5.0.2 on 2024-03-23 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0018_farmerprofile_is_verified_userprofile_is_verified_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="farmerprofile",
            name="farmer_profile_percentage",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
