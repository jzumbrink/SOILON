# Generated by Django 3.1.2 on 2020-10-19 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0004_auto_20201019_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bodenprobe',
            name='eingangsdatum',
        ),
        migrations.RemoveField(
            model_name='bodenprobe',
            name='pdf_erstellungsdatum',
        ),
    ]