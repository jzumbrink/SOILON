# Generated by Django 3.1.2 on 2020-10-29 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0012_auto_20201029_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kunde',
            name='hausnummer',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='telefonnummer',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
