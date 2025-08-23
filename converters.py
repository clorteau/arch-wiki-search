# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import lxml_html_clean
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
            #never called when in cache, applying different filter requires clearing cache
            text = await response.text()
        except Exception as e:
            #could not decode as text, send empty response
            #svgs will go through, not pngs or jpegs
            #FIXME: decide on this
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

class CleanHTMLConverter(RawConverter):
    @staticmethod
    def _convert_links(text, base_url, port):
            """Cleans up javascript, styles and excessive formattive
            """
            text = RawConverter._convert_links(text, base_url, port)
            text = lxml.html.clean.clean_html(text)
