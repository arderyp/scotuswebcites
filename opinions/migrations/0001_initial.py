# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('justices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=100)),
                ('discovered', models.DateTimeField(verbose_name=b'date discovered')),
                ('published', models.DateField(verbose_name=b'date published')),
                ('name', models.CharField(max_length=255)),
                ('pdf_url', models.URLField(max_length=255)),
                ('reporter', models.CharField(max_length=50, null=True, blank=True)),
                ('docket', models.CharField(max_length=20)),
                ('part', models.CharField(max_length=20)),
                ('justice', models.ForeignKey(to='justices.Justice', on_delete=models.CASCADE)),
            ],
        ),
    ]
