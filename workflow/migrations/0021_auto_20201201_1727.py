# Generated by Django 3.1.2 on 2020-12-01 16:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0020_ppmvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='bodenprobe',
            name='results_upload_time',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bodenprobe',
            name='label_name',
            field=models.CharField(default='Standard-Bodenprobe', max_length=50),
        ),
    ]
