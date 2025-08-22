# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

__version__ = '20250819'
__name__ = 'arch-wiki-search'
__author__ = 'Clem Lorteau'
__license__ = 'MIT'

__url__ = 'https://github.com/clorteau/arch-wiki-search'
__newwikirequesturl__ = 'https://#TODO'

import logging

class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;20m'
    yellow = '\x1b[33;20m'
    green = '\033[32m'
    red = '\x1b[31;20m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    # format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
    fields = ' %(message)s'

    FORMATS = {
        logging.DEBUG: grey + '🡪' + fields + reset,
        logging.INFO: green + '🡪' + fields + reset,
        logging.WARNING: yellow + '⚠' + fields + reset,
        logging.ERROR: red + '✖' + fields + reset,
        logging.CRITICAL: bold_red + '✖' + fields + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class AIOHTTPCustomFormatter(CustomFormatter):
    fields = '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

