# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from justices.models import Justice

def create_justices(apps, schema_editor):
    """Import baseline data for known justices"""

    justices = {
        'A':  'Samuel Alito',
        'AS': 'Antonin Scalia',
        'B': 'Stephen Breyer',
        'D': 'Decree',
        'DS': 'David Souter',
        'EK': 'Elana Kagan',
        'G': 'Ruth Bader Ginsburg',
        'JS': 'John Paul Stephens',
        'K': 'Anthony Kennedy',
        'PC': 'Per Curiam',
        'R': 'John G. Roberts',
        'SS': 'Sonia Sotomayor',
        'T': 'Clarence Thomas',
    }

    for id, name in justices.iteritems():
        justice = Justice(id=id, name=name)
        justice.save()

class Migration(migrations.Migration):

    dependencies = [
        ('justices', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_justices),
    ]
