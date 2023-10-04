# Generated by Django 4.2.5 on 2023-10-03 11:46

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("governanceplatform", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, default=None, max_length=30, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, default=None, max_length=30, null=True, region=None
            ),
        ),
    ]
