# -*- coding: utf-8 -*-

import os
import time
import logging

"""Logger for discovery process.

The default log level is INFO, but it can be switched to
DEBUG to troubleshoot tricky issues.  Each calndar day will
get it's own log file, so if the dicovery process is run
multiple times in a day, there will be one log file containing
that day's transactions.  The calendar day is the calendar day
on which the process was initiated, not the day the process completes
"""

class Logger(object):
    @staticmethod
    def initialize():
        yyyymmdd = time.strftime('%Y%m%d')
        current_directory = os.path.dirname(os.path.realpath(__file__))
        log_file = '%s/../logs/%s.log' % (current_directory, yyyymmdd)

        # Change level to logging.DEBUG to debug tricky issues
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(levelname)-8s : %(msg)s',
        )

    @classmethod
    def debug(cls, message):
        cls.initialize()
        logging.debug(message)

    @classmethod
    def info(cls, message):
        cls.initialize()
        logging.info(message)

    @classmethod
    def warning(cls, message):
        cls.initialize()
        logging.warning(message)

    @classmethod
    def error(cls, message):
        cls.initialize()
        logging.error(message)

    @classmethod
    def critical(cls, message):
        cls.initialize()
        logging.critical(message)
