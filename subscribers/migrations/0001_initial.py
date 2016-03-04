# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('subscribed', models.BooleanField()),
                ('hash_key', models.CharField(default=b'7657ebdd60ce68ff25ccfbeefdda97', unique=True, max_length=10)),
            ],
        ),
    ]
