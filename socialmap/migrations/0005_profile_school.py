# Generated by Django 5.1.7 on 2025-03-20 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmap', '0004_profile_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='school',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
