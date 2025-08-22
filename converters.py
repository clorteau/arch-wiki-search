# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

from aiohttp import web
from aiohttp_client_cache import CachedResponse
from __init__ import logger

class RawConverter:
    @staticmethod
    def _convert_links(text, base_url, port):
        """Converts the links that point to wiki being cached and proxied to the local caching proxy
        we're running
        """
        text = text.replace(base_url, f'http://localhost:{port}')

    @staticmethod
    async def convert(response, base_url, port):
        """Manipulates a aiohttp.ClientResponse to convert contents
        TODO: only convert if original response status is 200 ok, otherwise return an error page
        """

        text = None
        try:
            text = await response.text()
        except Exception as e:
            #could not decode as text, send empty response
            #svgs will go through, not pngs or jpegs
            #TODO: don't download them in the first place
            newresponse = web.Response(
                status = response.status,
                content_type = response.content_type
            )
        
        newresponse = web.Response(
            text = text,
            status = response.status,
            content_type=response.content_type
        )
        
        return newresponse