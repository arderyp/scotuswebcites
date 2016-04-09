# -*- coding: utf-8 -*-

import requests
from time import sleep
from urlparse import urlparse

from scotuswebcites import settings
from discovery.Logger import Logger


class Url:
    TIMEOUT = 30
    HEADERS = settings.REQ_HEADER
    SLEEP = 2

    @classmethod
    def get(cls, url=False, err=True):
        if url:
            # Wait 2 seconds between requests
            sleep(cls.SLEEP)
            check = urlparse(url)

            if not check.scheme:
                url = 'http://' + url 

            try:
                return requests.get(url, headers=cls.HEADERS, timeout=cls.TIMEOUT,)
            except Exception:
                pass
       
        if err:
            Logger.error('Fetching failed for: %s' % url)

        return False
