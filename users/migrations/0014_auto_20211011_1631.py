# Generated by Django 3.2.6 on 2021-10-11 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_city_country_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='status',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='country',
            name='status',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='state',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]