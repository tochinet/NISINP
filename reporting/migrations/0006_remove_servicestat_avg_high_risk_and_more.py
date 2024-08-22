# Generated by Django 5.1 on 2024-08-22 07:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reporting", "0005_servicestat_avg_high_risk_servicestat_high_risk_rate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="servicestat",
            name="avg_high_risk",
        ),
        migrations.RemoveField(
            model_name="servicestat",
            name="high_risk_rate",
        ),
        migrations.AddField(
            model_name="servicestat",
            name="avg_high_risk_treated",
            field=models.FloatField(
                default=0, verbose_name="Average high risks treated"
            ),
        ),
        migrations.AddField(
            model_name="servicestat",
            name="total_high_risks_treated",
            field=models.FloatField(default=0, verbose_name="Total high risks treated"),
        ),
    ]
