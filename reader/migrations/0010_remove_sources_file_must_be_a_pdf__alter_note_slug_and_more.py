# Generated by Django 5.1.2 on 2024-10-29 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0009_alter_note_slug'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='sources',
            name='File Must Be a PDF.',
        ),
        migrations.AlterField(
            model_name='note',
            name='slug',
            field=models.SlugField(blank=True, default='0jd02dr2xigwle85a0ei2p4s2ut3ovnhs3z5ud04b', max_length=255, unique=True),
        ),
        migrations.AddConstraint(
            model_name='sources',
            constraint=models.CheckConstraint(condition=models.Q(('pdf__iendswith', '.pdf')), name='pdf_format_check'),
        ),
    ]
