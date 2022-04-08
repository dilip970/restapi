# Generated by Django 3.2.6 on 2021-10-11 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_specializations_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='consultation_fee',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='experience',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
