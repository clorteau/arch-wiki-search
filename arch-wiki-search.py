#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

#TODO: convert html to text and markdown
#TODO: alternate browser
#TODO: conv = cleanhtml - custom css to clean up the page
#TODO: conv = darkhtml - custom css for dark mode
#TODO: conv = custom css - user supplied css
#TODO: pre-made --url --searchstring combinations for known wikis
#TODO: github feature request template to add new wikis
#TODO: arg to change number of days before cache expiry
#TODO: options to export and import cache
#TODO: readme

import sys
import asyncio
import argparse

from __init__ import __version__, __url__, __newwikirequesturl__, logger
from core import Core

async def main():
    await core.start()
    try:
        await core.search(search)
        await core.wait()
    except asyncio.CancelledError:
        print('')
        logger.info('Stopping')
    await core.stop()

if __name__ == '__main__':
    format_blue_underline = '\033[4;34m'
    format_reset = '\033[0m'
    parser = argparse.ArgumentParser(
        prog = sys.argv[0],
        description = 'Read and search Archwiki, online or offline, in HTML, markdown or text',
        epilog = f'Homepage: 🌐{format_blue_underline}{__url__}{format_reset}\
                   | Request to add new wiki: 🌐{format_blue_underline}{__newwikirequesturl__}{format_reset}',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--offline', default=False, action='store_true',
                         help='Don\'t try to go online, only used cached copy if it exists')
    parser.add_argument('--refresh', default=False, action='store_true',
                        help='Force going online and refresh the cache')
    parser.add_argument('-c', '--conv', default='raw',
                        choices=['raw', 'md', 'txt'],
                        #TODO: respect formatting
                        help='conversion mode:\n \
                              \traw: no conversion\n \
                              \tmd: convert to markdown\n \
                              \ttxt: convert to plain text')
    parser.add_argument('-b', '--browser',
        help='browser to use instead of user\'s default (ex: \'brave\', \'firefox\')',
        default=None, type=str)
    parser.add_argument('-u', '--url', default='https://wiki.archlinux.org',
                         help='URL of wiki to browse (ex: https://wikipedia.org, https://wiki.ubuntu.com)')
    parser.add_argument('-s', '--searchstring', default='/index.php?search=',
                         help='alternative search string \
                               (ex: \"/wiki/Special:Search?go=Go&search=\", \
                               \"/Home?action=fullsearch&value=\")')
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    parser.add_argument('-v', '--version', default=False, action='store_true')
    parser.add_argument('search', help='string to search (ex: \"installation guide\")', nargs='?',
                        const=None, type=str)
    args = parser.parse_args()
    if (args.version):
        print(__version__)
        sys.exit(0)
    if (not args.search):
        search = ''
    else:
        search = args.search

    core = Core(alt_browser=args.browser,
                conv=args.conv,
                base_url=args.url, 
                search_parm=args.searchstring,
                offline=args.offline,
                refresh=args.refresh,
                debug=args.debug
                )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass #exception CancelledError will be caught in main