# Generated by Django 3.2.6 on 2021-09-01 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210827_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appoinment_timings',
            name='slot_date',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='appoinment_timings',
            name='slot_time',
            field=models.TextField(null=True),
        ),
    ]