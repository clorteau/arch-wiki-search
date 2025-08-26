# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

__version__ = '20250826'
__name__ = 'arch_wiki_search'
__author__ = 'Clem Lorteau'
__license__ = 'MIT'

__contact__ = '@northernlights:matrix.lorteau.fr'
__url__ = 'https://github.com/clorteau/arch-wiki-search'
__newwikirequesturl__ = 'https://github.com/clorteau/arch-wiki-search/issues/new?template=new-wiki.md'

import logging

class Colors:
    grey = '\x1b[38;20m'
    yellow = '\x1b[33;20m'
    green = '\033[32m'
    red = '\x1b[31;20m'
    bold = '\033[1m'
    bold_red = '\x1b[31;1m'
    blue_underline = '\033[4;34m'
    reset = '\x1b[0m'

class CustomFormatter(logging.Formatter):
    # format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
    fields = ' %(message)s'

    FORMATS = {
        logging.DEBUG: Colors.grey + fields + Colors.reset,
        logging.INFO: Colors.green + '🡪' + fields + Colors.reset,
        logging.WARNING: Colors.yellow + '⚠' + fields + Colors.reset,
        logging.ERROR: Colors.red + '✖' + fields + Colors.reset,
        logging.CRITICAL: Colors.bold_red + '✖✖' + fields + Colors.reset
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

