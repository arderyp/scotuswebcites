# Generated by Django 2.1.7 on 2019-03-02 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opinions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opinion',
            name='discovered',
            field=models.DateTimeField(verbose_name='date discovered'),
        ),
        migrations.AlterField(
            model_name='opinion',
            name='published',
            field=models.DateField(verbose_name='date published'),
        ),
    ]
