# Generated by Django 5.1 on 2024-09-09 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("incidents", "0010_alter_questioncategorytranslation_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="name",
            field=models.CharField(
                default="[MISSING_TRANSLATION", max_length=255, verbose_name="Name"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="emailtranslation",
            name="subject",
            field=models.CharField(
                default="[MISSING_TRANSLATION]", max_length=255, verbose_name="Subject"
            ),
            preserve_default=False,
        ),
    ]
