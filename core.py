# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import sys
import logging
import asyncio
import traceback
import webbrowser
import urllib.parse
from cachingproxy import CachingProxy
from __init__ import __name__, logger

class Core:
    """Manages the caching proxy in async context and launches the appropriate browser
    """
    base_url = ''
    search_parm = ''
    current_url = ''
    search_term = ''
    cachingproxy = None
    offline = False
    refresh = False
    debug = False
    _stop = False
    
    async def start(self):
        try:
            await self.cachingproxy.start()
        except Exception as e:
            logger.error(f'Failed to start caching proxy:\n{e}')
            if self.debug:
                print(traceback.format_exc())
            sys.exit(-3)

    async def search(self, search_term = ''):
        url_path = ''
        if search_term != '':
            url_path = self.search_parm + urllib.parse.quote_plus(search_term)
        await self._go(url_path)

    async def _go (self, url_path):
        if (not self.base_url.startswith(('http://', 'https://'))):
            err = f'Unsupported url: {self.base_url}'
            logger.error(err)
            sys.exit(-2)

        dest_url = f'{self.base_url}{url_path}'
        logger.debug(f'Caching and serving {dest_url}')

        #retrieve and if needed cache the requested page before the browser is called
        await self.cachingproxy.fetch(url_path)

        try:
            webbrowser.open(f'http://localhost:{self.cachingproxy.port}/{dest_url}')
        except Exception as e:
            logger.error(f'Failed to start browser: {e}')
            if self.debug:
                print(traceback.format_exc())
        else:
            self.current_url = dest_url
            logger.debug('Calling browser')

    async def stop(self):
        self._stop = True
        await self.cachingproxy.stop()

    async def wait(self):
        """keep main thread active and proxy running in separate thread until told to stop
        TODO: condition to stop
        """
        try:
            await self._sleep()
        except KeyboardInterrupt:
            logger.info('Stopping')
            await self.stop()

    async def _sleep(self, secs=2):
        """Sleep and check for stop condition every X seconds
        TODO: proper stop condition
        """
        while not self._stop:
            await asyncio.sleep(secs)

    def __init__(self, base_url = 'https://wiki.archlinux.org',
                 search_parm = '/index.php?search=',
                 alt_browser = '', conv = 'raw',
                 offline=False, refresh=False, debug=False):
        if not base_url.endswith('/'):
            base_url += '/' #so relative links work
        self.base_url = base_url
        self.search_parm = search_parm
        self.conv = conv
        self.offline = offline
        self.refresh = refresh
        self.debug = debug

        if self.debug: logger.setLevel(logging.DEBUG)
        else: logger.setLevel(logging.INFO)

        self.cachingproxy = CachingProxy(self.base_url, debug=debug)

