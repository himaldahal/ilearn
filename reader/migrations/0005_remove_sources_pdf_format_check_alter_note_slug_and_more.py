# Generated by Django 5.1.2 on 2024-10-29 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0004_alter_note_slug'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='sources',
            name='pdf_format_check',
        ),
        migrations.AlterField(
            model_name='note',
            name='slug',
            field=models.SlugField(blank=True, default='yy4sn0sjmbuar7w6v5f4m9dqbi3pbgaesiwy3fnhdy47cuu0yn', max_length=255, unique=True),
        ),
        migrations.AddConstraint(
            model_name='sources',
            constraint=models.CheckConstraint(condition=models.Q(('pdf__iendswith', '.pdf')), name='File Must Be a PDF.'),
        ),
    ]
