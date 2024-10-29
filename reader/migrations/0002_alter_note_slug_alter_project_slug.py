# Generated by Django 5.1.2 on 2024-10-29 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='slug',
            field=models.SlugField(blank=True, default='2amjmq65x5t3lyjuh6ofkb1ud99ioi773fvt6bk1rvi8489b', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
