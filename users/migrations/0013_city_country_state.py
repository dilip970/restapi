# Generated by Django 3.2.7 on 2021-10-11 10:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_doctor_consultation_fee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('country_name', models.CharField(max_length=100)),
                ('createdBy', models.CharField(default='system', max_length=30)),
                ('updatedBy', models.CharField(default='system', max_length=30)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('state_name', models.CharField(max_length=100)),
                ('createdBy', models.CharField(default='system', max_length=30)),
                ('updatedBy', models.CharField(default='system', max_length=30)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.country')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('city_name', models.CharField(max_length=100)),
                ('createdBy', models.CharField(default='system', max_length=30)),
                ('updatedBy', models.CharField(default='system', max_length=30)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.country')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.state')),
            ],
        ),
    ]
