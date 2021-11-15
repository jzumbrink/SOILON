# Generated by Django 3.1.2 on 2020-10-19 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20201014_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kunde',
            name='addresszusatz',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='email',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='geburtstag',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='geschlecht',
            field=models.CharField(default='nicht angegeben', max_length=20),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='hausnummer',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='plz',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='strasse',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='telefonnummer',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='titel',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='kunde',
            name='wohnort',
            field=models.CharField(default='', max_length=50),
        ),
    ]