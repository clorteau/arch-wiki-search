# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import sys
import logging
import asyncio
import traceback
import webbrowser
import urllib.parse
import subprocess
# from multiprocessing import Process, Manager
from concurrent.futures import ThreadPoolExecutor

try:
    from __init__ import __logger__, __icon__, Colors
    from exchange import StopFlag
    from cachingproxy import LazyProxy
except ModuleNotFoundError:
    from arch_wiki_search import __logger__, __icon__, Colors
    from arch_wiki_search.exchange import StopFlag
    from arch_wiki_search.cachingproxy import LazyProxy
    from arch_wiki_search.wikis import Wikis

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
    noicon = False
    _notifIconStarted = False 
    _stop = False #will shutdown if set to True
    
    async def start(self):
        try:
            await self.proxy.start()
        except Exception as e:
            __logger__.error(f'Failed to start caching proxy:\n{e}')
            if self.debug:
                print(traceback.format_exc())
            sys.exit(-3)
        msg = f'Serving wiki on http://localhost:{self.proxy.port} - {Colors.yellow}<ctrl-c>{Colors.green}'
        if self._notifIconStarted:
            msg += f' or {__icon__}{Colors.yellow}🡪 Exit{Colors.green}'
        msg += ' to stop'
        __logger__.info(msg)
        await self.proxy.printcachesize()

    async def search(self, search_term = ''):
        url_path = ''
        if search_term != '':
            url_path = self.search_parm + urllib.parse.quote_plus(search_term)
        await self._go(url_path)

    def spawnIcon(self):
        if (not self.noicon) and ('DISPLAY' in os.environ): #GUI, no --noicon
            try:
                from PyQt6.QtWidgets import QApplication
            except ModuleNotFoundError:
                __logger__.error('PyQT6 not found, not showing a notification icon')
            else:
                __logger__.info('Spawning notification icon')
                # run the QT app loop in a subprocess
                try:
                    path = os.path.dirname(os.path.realpath(__file__)) + '/notification.py'
                    process = subprocess.Popen(['python', path])
                except Exception as e:
                    msg = f'Failed to start notification icon: {e}'
                    __logger__.error(msg)
                self._notifIconStarted = True

    def _openbrowser(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            __logger__.error(f'Failed to start browser: {e}')
            if self.debug:
                print(traceback.format_exc())
        else:
            self.current_url = url
            __logger__.debug('Calling browser')

    async def _go (self, url_path):
        if (not self.base_url.startswith(('http://', 'https://'))):
            err = f'Unsupported url: {self.base_url}'
            __logger__.error(err)
            sys.exit(-2)

        dest_url = f'{self.base_url}{url_path}'
        __logger__.debug(f'Caching and serving {dest_url}')

        #retrieve and if needed cache the requested page before the browser is called
        await self.proxy.fetch(url_path)

        #open browser asynchronously as otherwise the code would be blocking when there's no graphical
        #environment
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor,
                self._openbrowser, f'http://localhost:{self.proxy.port}/{dest_url}')
        
    async def stop(self):
        self._stop = True
        await self.proxy.stop()
        await self.proxy.printcachesize()
        self.stopFlag.delete()

    async def wait(self, secs=1):
        """Sleep and check for stop flag every X seconds
        """
        while not self._stop:
            flag = self.stopFlag.read()
            if flag == True:
                self._stop = True
                break
            await asyncio.sleep(secs)

    def __init__(self, knownwikis,
                 base_url=None, search_parm=None,
                 alt_browser='', conv='', wiki='archwiki',
                 offline=False, refresh=False, debug=False, noicon=False):
        """base_url (option -u) will override -wiki.url
        search_parm (option -s) will override -wiki.searchstring
        """
        self.stopFlag = StopFlag() #will be written to True by the QT gui to stop the proxy

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
        self.noicon = noicon

        if self.debug: __logger__.setLevel(logging.DEBUG)
        else: __logger__.setLevel(logging.INFO)
        
        self.proxy = LazyProxy(self.base_url, debug=debug, conv=self.conv)

