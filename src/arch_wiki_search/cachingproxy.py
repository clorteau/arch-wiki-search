# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import sys
import socket
import logging
import asyncio
import traceback
from datetime import timedelta
from collections import Counter
from aiohttp import web, DummyCookieJar, TraceConfig
from concurrent.futures import ThreadPoolExecutor
from aiohttp_client_cache import CachedSession, FileBackend

try:
    import converters
    from __init__ import __logger__, __version__, __name__, __url__, __contact__, __icon__, Colors
except ModuleNotFoundError:
    from arch_wiki_search import converters, __logger__, __version__, __url__, __contact__, __icon__, Colors

class LazyProxy:
    """Asynchronous caching http proxy that caches for a long time, manipulates responses,
    and only serves one top domain
    """
    useragent = f'{__name__}/{__version__} ({__url__}; {__contact__}) python-aio-http-cache'
    base_url = ''
    cache_dir = ''
    expire_days = 8
    cache = None
    app = None
    debug = False
    port = 8888 #will be set to available port by start()
    runner = None

    def _hsize(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f}{unit}"
            size /= 1024

    async def _printcachesize(self):
        def _dirsize(path):
            size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    size += os.path.getsize(fp)
            return size
        # run above blocking code asynchronously on executor
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, _dirsize, self.cache_dir)
            __logger__.info(f'{Colors.grey}Cache size: {self._hsize(result)}{Colors.reset}')

    async def printcachesize(self):
        """Asynchronously calculate total cache size and output in human readable format
        """
        assert self.cache_dir != ''
        await self._printcachesize()
    
    async def start(self):
        assert self.cache != None            
        server = web.Server(self._get_handler, debug=self.debug)

        #find available port number to bind to
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))  # 0 = available port
        port = sock.getsockname()[1]
        sock.close()
        self.port = port

        #start in separate thread
        self.runner = web.ServerRunner(server)
        if (self.debug): logging.basicConfig(level=logging.DEBUG)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()

    async def stop(self):
        __logger__.info('Stopping')
        await self.runner.cleanup()
        await self.cache.close()

    async def clear(self):
        await self.cache.clear()

    async def _on_fetch_request_end(self, session, trace_config_ctx, params):
        __logger__.debug(f'Request: {params}')

    async def _fetch(self, urlpath):
        url = self.base_url + '/' + urlpath
        resp = None
        ignore_cookies = DummyCookieJar()
        trace_config = TraceConfig()
        trace_config.on_request_end.append(self._on_fetch_request_end)
        async with CachedSession(cache=self.cache,
                                 cookie_jar=ignore_cookies,
                                 trace_configs=[trace_config]) as session:
            try:
                resp = await session.get(f'{url}', headers={'User-Agent': self.useragent,
                                                            'Accept-Encoding': 'gzip'})
            except Exception as e:
                msg = f'Failed to fetch URL: {url}'
                trace = traceback.format_exc()
                __logger__.error(f'{msg}\n{e}')
                text = f'\
                    <!DOCTYPE html><html>\
                    <h3>{msg}</h3>'
                if (self.debug): text += f'<code>{trace.replace('\n', '<br/>\n')}</code>'
                text += '</html>'
                return web.Response(content_type='text/html', text=text)
            await session.close()
        # logger.debug(f'Request: {resp.request_info.headers}')
        return resp

    async def fetch(self, urlpath):
        """Retrieves contents at base_url/urlpath
        """
        resp = await self._fetch(urlpath)
        assert resp != None
        expires = resp.expires.isoformat() if resp.expires else 'Never'
        __logger__.debug(f'{resp.url} expires: {expires}')
        return resp

    async def _get_handler(self, request, ):
        """Fetches the requested page, manipulates it and responds with it
        Also caches one level of links in the background
        """
        __logger__.debug(f'Got request: {request}')

        #the full URL to fetch is passed as the request's path; extract the target path
        url = request.raw_path
        url = url.lstrip('/')
        path = url.replace(self.base_url, '')

        response = await self.fetch(path)

        # convert result
        if self.conv == 'raw':
            converter = converters.RawConverter(response, self.base_url, self.port)
        elif self.conv == 'clean':
            converter = converters.CleanHTMLConverter(response, self.base_url, self.port)
        elif self.conv == 'txt':
            converter = converters.TxtConverter(response, self.base_url, self.port)
        elif self.conv == 'md':
            converter = converters.MDConverter(response, self.base_url, self.port)
        elif self.conv == 'basic':
            converter = converters.BasicHTMLConverter(response, self.base_url, self.port)
        else:
            converter = converters.RawConverter(response, self.base_url, self.port)
        newresponse = await converter.convert()

        # silently try and pre-cache one level of links in separate threads
        links = converters.RawConverter(newresponse, self.base_url, self.port).gethrefs()
        if self.previouslinks == None: 
            self.previouslinks = links
        # don't do it recursively
        else:
            if Counter(links) != Counter(self.previouslinks):
                for link in links:
                    if link.startswith('/'): link = link[1:]
                    __logger__.debug(f'Precaching {link}')
                    asyncio.create_task(self._fetch(link)) #don't wait for it

        await newresponse.prepare(request)
        return newresponse

    def __init__(self, base_url, cache_dir='', expire_days=30, debug=False, conv=''):
        self.base_url = base_url
        self.expire_days = expire_days
        self.cache_dir = cache_dir
        self.debug = debug
        self.conv = conv
        self.previouslinks = None

        if (not self.base_url.startswith(('http://', 'https://'))):
            err = f'Unsupported url: {self.base_url}'
            __logger__.error(err)
            sys.exit(-2)

        if os.name == 'posix': 
            self.cache_dir = os.path.join(os.path.expanduser('~'), '.cache', __name__)
        elif os.name == 'nt': 
            self.cache_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', __name__)

        if os.path.isdir(self.cache_dir):
            if os.access(self.cache_dir, os.W_OK):
                __logger__.debug(f'The cache directory {self.cache_dir} exists and is writable')
            else:
                err = f'The cache directory {self.cache_dir} is not writable'
                __logger__.critical(err)
                print(traceback.format_exc())
                sys.exit(-4)
        else:
            try:
                os.makedirs(self.cache_dir)
                __logger__.info(f'Created cache directory {self.cache_dir}')
            except Exception as e:
                __logger__.critical(f'Failed to create cache directory {self.cache_dir}')
                print(traceback.format_exc())
                sys.exit(-4)

        self.cache = FileBackend(
            cache_name = self.cache_dir,
            expire_after = timedelta(days=self.expire_days),
            autoclose=False,
            #only cache these responses
            allowed_codes = (200, #ok
                             301, #permanent move
                             308, #permanent redirect
                            ),
        )

        
