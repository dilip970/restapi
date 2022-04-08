# Generated by Django 3.2.6 on 2021-10-13 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_doctor_specialization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.city'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='patient',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.country'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='patient',
            name='state',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.state'),
            preserve_default=False,
        ),
    ]
