# Generated by Django 5.1.2 on 2024-11-05 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0020_remove_note_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-id'], 'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
        migrations.AlterModelOptions(
            name='sources',
            options={'verbose_name': 'Source', 'verbose_name_plural': 'Sources'},
        ),
    ]
