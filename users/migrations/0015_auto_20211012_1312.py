# Generated by Django 3.2.6 on 2021-10-12 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20211011_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.country'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doctor',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.city'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.state'),
        ),
    ]
