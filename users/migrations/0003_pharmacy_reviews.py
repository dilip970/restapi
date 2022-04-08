# Generated by Django 3.2.5 on 2021-08-03 12:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210802_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pharmacy_Reviews',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('review_starts', models.IntegerField(default=0, null=True)),
                ('review_text', models.TextField(null=True)),
                ('identifier', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('createdBy', models.CharField(default='system', max_length=30)),
                ('updatedBy', models.CharField(default='system', max_length=30)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.patient')),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.pharmacy')),
            ],
        ),
    ]
