# -*- coding: utf-8 -*-

import time
import hashlib
from django.db import models


def create_hash():
    """This function generate 10 character long hash"""
    hash_key = hashlib.sha1()
    time_string = str(time.time())
    hash_key.update(time_string.encode('utf-8'))
    return hash_key.hexdigest()[:20]


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=False)
    hash_key = models.CharField(max_length=20, unique=True)

    def _set_hash(self):
        self.hash_key = create_hash()
