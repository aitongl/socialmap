# Generated by Django 5.1.6 on 2025-03-16 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialmap', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_name',
        ),
    ]
