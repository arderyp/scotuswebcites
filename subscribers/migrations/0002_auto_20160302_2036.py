# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(unique=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='hash_key',
            field=models.CharField(default=b'20a6ed032d486b9c244d', unique=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='subscribed',
            field=models.BooleanField(default=False),
        ),
    ]
