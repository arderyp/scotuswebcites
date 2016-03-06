# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opinions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermaFolder',
            fields=[
                ('folder_id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('opinion', models.ForeignKey(to='opinions.Opinion')),
            ],
        ),
    ]
