# Generated by Django 5.1.2 on 2024-10-29 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0006_alter_note_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='slug',
            field=models.SlugField(blank=True, default='p6q9k76kmke8xfqofbn4b017quzaf9jstadgy0j1dl2rcs514fniv7e9nwon', max_length=255, unique=True),
        ),
    ]