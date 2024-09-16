# Generated by Django 5.0.2 on 2024-03-20 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0014_user_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="partnerprofile",
            name="address",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="partnerprofile",
            name="partner_profile_percentage",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
