# Generated by Django 3.2.6 on 2021-10-11 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_doctor_specialization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specializations',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]