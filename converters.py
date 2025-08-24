# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import lxml_html_clean
from aiohttp import web
from aiohttp_client_cache import CachedResponse
from bs4 import BeautifulSoup
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

class CleanHTMLConverter(RawConverter):
    async def convert(self):
        """Cleans up javascript, styles and excessive formattive
        """
        try:
            self.text = await self.response.text()
        except Exception as e:
            msg = 'Error reading response from server: ' + str(e)
            logger.warning(msg)
            self.newresponse.text = msg
            return self.newresponse
        
        self.text = self._links_to_local() 
        #self.text = lxml_html_clean.clean_html(self.text)
         # Parse the HTML content
        soup = BeautifulSoup(self.text, features='xml')
        # Remove <script> tags
        for script in soup.find_all('script'):
            script.decompose()
        # Remove <iframe> and <frame> tags
        for frame in soup.find_all(['iframe', 'frame']):
            frame.decompose()
        # Remove all <style> tags
        # for style in soup.find_all('style'):
        #     style.decompose()
        # Get the cleaned HTML
        self.text = soup.prettify()  # Use prettify for better formatting
        self.newresponse.text = self.text
        return self.newresponse
