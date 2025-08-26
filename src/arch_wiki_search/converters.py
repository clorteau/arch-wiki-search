# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import warnings
import html5lib
import lxml_html_clean
from aiohttp import web
from aiohttp_client_cache import CachedResponse
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

try:
    from __init__ import logger
except ModuleNotFoundError:
    from arch_wiki_search import logger
    
class RawConverter:
    """Manipulates a aiohttp.ClientResponse to convert contents
    TODO: only convert if original response status is 200 ok, otherwise return an error page
    """

    def gethrefs(self) -> [str]:
        """Returns list of local links referenced to by response
        """
        hrefs = []
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(self.response.text, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            url = link.get('href')
            if url.startswith(self.base_url) or url.startswith('/'):
                hrefs.append(url)
        return hrefs

    def _links_to_local(self) -> str:
        """Rewrite links by appending them to our local proxy
        """
        return self.text.replace(self.base_url, f'http://localhost:{self.port}')

    def __init__(self, response: CachedResponse, base_url: str, port: int):
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
            logger.debug(msg)
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
            self.newresponse.text = msg
            return self.newresponse
        self.text = super()._links_to_local()

        bs = BeautifulSoup(self.text, 'lxml')
        for tag in bs.find_all('script', 'iframe', 'frame', 'style'):
            tag.decompose()
        text = bs.get_text()

        # remove extra new lines
        text = text.replace('\r\n\r\n\r\n', '\r\n\r\n')
        text = text.replace('\n\n\n', '\n\n')

        self. text = text
        self.newresponse.text = self.text
        self.newresponse.content_type = 'text/plain'
        return self.newresponse