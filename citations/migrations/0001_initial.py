# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opinions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scraped', models.URLField(max_length=255)),
                ('scrape_evaluation', models.CharField(default='gs', max_length=2, choices=[('gs', 'good scrape'), ('bs', 'bad scrape'), ('bc', 'bad citation')])),
                ('status', models.CharField(default='a', max_length=1, choices=[('a', 'available'), ('u', 'unavailable'), ('r', 'redirect')])),
                ('validated', models.URLField(max_length=255, null=True)),
                ('verify_date', models.DateTimeField(null=True, verbose_name='date verified')),
                ('memento', models.URLField(max_length=255, null=True)),
                ('webcite', models.URLField(max_length=255, null=True)),
                ('perma', models.URLField(max_length=255, null=True)),
                ('opinion', models.ForeignKey(to='opinions.Opinion')),
            ],
        ),
    ]
