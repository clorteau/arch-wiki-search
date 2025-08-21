#!/bin/sh

import os
import sys
import logging
import traceback
from aiohttp import web, DummyCookieJar
from datetime import timedelta
from aiohttp_client_cache import CachedSession, FileBackend
from __init__ import __name__, logger

class CachingProxy:
    """Asynchronous caching http proxy that caches for a long time, manipulates responses,
    and only serves one top domain
    """
    base_url = ''
    cache_dir = ''
    expire_days = 8
    cache = None
    app = None
    debug = False
    port = 8888 #TODO: set to available port automatically
    runner = None

    def _hsize(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
        size /= 1024

    async def _printcachesize(self):
        def _printdirsize(path):
            size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    size += os.path.getsize(fp)
            logger.info(f'Cache size:{self._hsize(size)}')

        coro = asyncio.to_thread(_printdirsize(self.cache_dir))
        task = asyncio.create_task(coro)
        await asyncio.sleep(0)
        await task

    def printcachesize(self):
        """Asynchronously calculate total cache size and output in human readable format
        """
        assert self.cache_dir != ''
        asyncio.run(self._printcachesize())
    
    async def start(self):
        assert self.cache != None            
        server = web.Server(self._get_handler, debug=self.debug)

        #start in separate thread
        self.runner = web.ServerRunner(server)
        if (self.debug): logging.basicConfig(level=logging.DEBUG)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
    
        logger.info(f'Serving wiki on http://localhost:{self.port}')

    async def stop(self):
        await self.runner.cleanup()

    async def fetch(self, urlpath):
        #TODO: pre-cache one-level of links
        url = self.base_url + urlpath
        resp = None
        ignore_cookies = DummyCookieJar()
        async with CachedSession(cache=self.cache, cookie_jar=ignore_cookies) as session:
            try:
                resp = await session.get(f'{url}')
            except Exception as e:
                msg = f'Failed to fetch URL: {url}'
                trace = traceback.format_exc()
                logger.error(f'{msg}\n{e}')
                text = f'\
                    <!DOCTYPE html><html>\
                    <h3>{msg}</h3>'
                if (self.debug): text += f'<code>{trace.replace('\n', '<br/>\n')}</code>'
                text += '</html>'
                return web.Response(content_type='text/html', text=text)
        assert resp != None
        expires = resp.expires.isoformat() if resp.expires else 'Never'
        logger.debug(f'{resp.url} expires: {expires}')
        
        return resp

    async def _get_handler(self, request):
        logger.debug(f'Got request: {request}')

        #the full URL to fetch is passed as the request's path; extract the target path
        url = request.raw_path
        url = url.lstrip('/')
        path = url.replace(self.base_url, '')

        response = await self.fetch(path)
        #TODO: manipulate response (rewrite links, conversions...)
        text = await response.text() #FIXME: throws exception when trying to get a png
        newresponse = web.Response(
            text=text,
            status = response.status,
            content_type=response.content_type
        )
        await newresponse.prepare(request)
        return newresponse

    def __init__(self, base_url, cache_dir='', expire_days=8, debug=False):
        self.base_url = base_url
        self.expire_days = expire_days
        self.cache_dir = cache_dir
        self.debug = debug

        if (not self.base_url.startswith(('http://', 'https://'))):
            err = f'Unsupported url: {self.base_url}'
            logger.error(err)
            sys.exit(-2)

        if os.name == 'posix': 
            self.cache_dir = os.path.join(os.path.expanduser('~'), '.cache', __name__)
        elif os.name == 'nt': 
            self.cache_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', __name__)

        if os.path.isdir(self.cache_dir):
            if os.access(self.cache_dir, os.W_OK):
                logger.debug(f'The cache directory {self.cache_dir} exists and is writable')
            else:
                err = f'The cache directory {self.cache_dir} is not writable'
                logger.error(err)
                print(traceback.format_exc())
                sys.exit(-4)
        else:
            try:
                os.makedirs(self.cache_dir)
                logger.info(f'Created cache directory {self.cache_dir}')
            except Exception as e:
                logger.error(f'Failed to create cache directory {self.cache_dir}')
                print(traceback.format_exc())
                sys.exit(-4)

        self.cache = FileBackend(
            cache_name = self.cache_dir,
            expire_after = timedelta(days=self.expire_days),
            #only cache these responses
            allowed_codes = (200, #ok
                             301, #permanent move
                             308, #permanent redirect
                            ),
        )

        # self.printcachesize()

        
