# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Justice',
            fields=[
                ('id', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]
