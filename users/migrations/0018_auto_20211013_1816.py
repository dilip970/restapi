# Generated by Django 3.2.6 on 2021-10-13 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20211013_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.city'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.country'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.state'),
        ),
    ]