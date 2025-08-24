# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import warnings
import html5lib
import html2text
import lxml_html_clean
from aiohttp import web
from aiohttp_client_cache import CachedResponse
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from __init__ import logger

class RawConverter:
    """Manipulates a aiohttp.ClientResponse to convert contents
    TODO: only convert if original response status is 200 ok, otherwise return an error page
    """
    def _links_to_local(self):
        """Rewrite links by appending them to our local proxy
        """
        return self.text.replace(self.base_url, f'http://localhost:{self.port}')

    def __init__(self, response, base_url, port):
        self.base_url = base_url
        self.port = port
        newresponse = web.Response(status=response.status, content_type=response.content_type)
        self.response = response  
        self.newresponse = newresponse

    async def convert(self):
        try:
            self.text = await self.response.text()
        except Exception as e:
            msg = 'Error reading response from server: ' + str(e)
            logger.warning(msg)
            self.newresponse.text = msg
            return self.newresponse
        self.text = self._links_to_local()
        self.newresponse.text = self.text
        return self.newresponse

class CleanHTMLConverter(RawConverter):
    async def convert(self):
        """Cleans up javascript, styles and excessive formattive format
        """
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        try:
            self.text = await self.response.text()
        except Exception as e:
            msg = 'Error reading response from server: ' + str(e)
            logger.warning(msg)
            self.newresponse.text = msg
            return self.newresponse
        self.text = super()._links_to_local()
        try:
            soup = BeautifulSoup(self.text, 'lxml')
        except XMLParsedAsHTMLWarning:
            soup = BeautifulSoup(self.text, 'html5lib')
        for tag in soup.find_all('script', 'iframe', 'frame', 'style'):
            tag.decompose()
        self.text = soup.prettify()  # better formatting
        self.newresponse.text = self.text
        return self.newresponse

class TxtConverter(RawConverter):
    async def convert(self):
        """Only keeps text
        """
        try:
            self.text = await self.response.text()
        except Exception as e:
            msg = 'Error reading response from server: ' + str(e)
            logger.warning(msg)
            self.newresponse.text = msg
            return self.newresponse
        self.text = super()._links_to_local()

        # self.text = html2text.html2text(self.text)

        bs = BeautifulSoup(self.text, 'lxml')
        for tag in bs.find_all('script', 'iframe', 'frame', 'style'):
            tag.decompose()
        self.text = bs.get_text()

        self.newresponse.text = self.text
        self.newresponse.content_type = 'text/plain'
        return self.newresponse