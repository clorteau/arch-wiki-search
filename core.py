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
from concurrent.futures import ThreadPoolExecutor
from __init__ import __name__, logger
import wikis

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

        await self.cachingproxy.printcachesize()

    async def search(self, search_term = ''):
        url_path = ''
        if search_term != '':
            url_path = self.search_parm + urllib.parse.quote_plus(search_term)
        await self._go(url_path)

    def _openbrowser(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.error(f'Failed to start browser: {e}')
            if self.debug:
                print(traceback.format_exc())
        else:
            self.current_url = url
            logger.debug('Calling browser')

    async def _go (self, url_path):
        if (not self.base_url.startswith(('http://', 'https://'))):
            err = f'Unsupported url: {self.base_url}'
            logger.error(err)
            sys.exit(-2)

        dest_url = f'{self.base_url}{url_path}'
        logger.debug(f'Caching and serving {dest_url}')

        #retrieve and if needed cache the requested page before the browser is called
        await self.cachingproxy.fetch(url_path)

        #open browser asynchronously as otherwise the code would be blocking when there's no graphical
        #environment
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor,
                self._openbrowser, f'http://localhost:{self.cachingproxy.port}/{dest_url}')
        
    async def stop(self):
        self._stop = True
        await self.cachingproxy.stop()
        await self.cachingproxy.printcachesize()

    async def wait(self, secs=2):
        """Sleep and check for stop condition every X seconds
        TODO: proper stop condition
        """
        while not self._stop:
            # if keyboard.is_pressed('q'): self._stop = true #bs needs root
            await asyncio.sleep(secs)

    def __init__(self, knownwikis,
                 base_url=None, search_parm=None,
                 alt_browser='', conv='', wiki='archwiki',
                 offline=False, refresh=False, debug=False, ):
        """base_url (option -u) will override -wiki.url
        search_parm (option -s) will override -wiki.searchstring
        """
        assert knownwikis
        for w in knownwikis:
            if w.name == wiki:
                self.base_url = w.url
                self.search_parm = w.searchstring
                break
            
        if base_url:
            self.base_url = base_url
        if search_parm:
            self.search_parm = search_parm
        self.conv = conv
        self.offline = offline
        self.refresh = refresh
        self.debug = debug

        if self.debug: logger.setLevel(logging.DEBUG)
        else: logger.setLevel(logging.INFO)

        self.cachingproxy = CachingProxy(self.base_url, debug=debug, conv=self.conv)

