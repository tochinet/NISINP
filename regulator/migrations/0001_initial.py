# Generated by Django 4.2 on 2023-05-04 06:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegulatorUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_phone_number', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Regulator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regulator_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('regulator_identifier', models.CharField(max_length=64)),
                ('regulator_name', models.CharField(max_length=64)),
                ('regulator_country', models.CharField(max_length=64)),
                ('regulator_adress', models.CharField(max_length=255)),
                ('regulator_email', models.CharField(blank=True, max_length=100, null=True)),
                ('regulator_phone_number', models.CharField(blank=True, max_length=30, null=True)),
                ('regulator_monarc_path', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('sector_name', models.CharField(max_length=100)),
                ('sector_parent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='regulator.sector')),
                ('sector_regulator_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='regulator.regulatoruser')),
            ],
        ),
    ]
