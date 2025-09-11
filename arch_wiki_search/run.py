# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

#TODO: conv = darkhtml - custom css for dark mode
#TODO: conv = custom css - user supplied css
#TODO: arg to change number of days before cache expiry
#TODO: read command line args from conf file
#TODO: option to select language
#TODO: test mode
#TODO: refresh mode
#TODO: converters: keep only article content (tag main, id=content?)
#TODO: text mode corner icon - maybe try TK or curses instead of Textual (looks great but no multiplexing/overlaying?)

import os
import sys
import asyncio
import argparse

try:
    import arch_wiki_search
except ModuleNotFoundError:
    print('I\'m part of a package, I need to be loaded as such then run as a script: \'python -m arch_wiki_search.run\'')
    sys.exit(-1)

from arch_wiki_search import __version__, __url__, __newwikirequesturl__, __logger__, __icon__, Colors, PACKAGE_NAME
from arch_wiki_search.exchange import ZIP
from arch_wiki_search.core import Core
from arch_wiki_search.wikis import Wikis

async def _main(core, search):
    core.spawnIcon()
    await core.start()
    try:
        await core.search(search)
        await core.wait()
    except asyncio.CancelledError:
        print('')
    
    await core.stop()

async def _clear(core):
    """Clear the cache
    """
    await core.proxy.printcachesize()
    __logger__.warning('This will clear your cache - are you sure? (type \'Yes\')')
    a = input ('> ')
    if a != 'Yes': sys.exit(-7)
    await core.proxy.clear()
    await core.proxy.printcachesize()

def main():
    """Load pre-configured base_url/searchstring pairs from yaml file, process arguments,
    start core and notif icon and close them cleanly
    """
    knownwikis = None
    debug = False
    if '-d' in sys.argv: debug = True
    try:
        knownwikis = Wikis(debug=debug)
    except Exception as e:
        __logger__.error(e)
        print(knownwikis.gethelpstring())
        sys.exit(-6)
    
    parser = argparse.ArgumentParser(
        prog = PACKAGE_NAME,
        description = f'''Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal 

Examples:
    {Colors.yellow}🡪 {Colors.reset}{PACKAGE_NAME} \"installation guide\"{Colors.reset}
    {Colors.yellow}🡪 {Colors.reset}{PACKAGE_NAME} --wiki=wikipedia --conv=txt \"MIT license\"{Colors.reset}''',
        epilog = f'''Options -u and -s overwrite the corresponding url or searchstring provided by -w
Known wiki names and their url/searchstring pairs are read from a \'{knownwikis.filename}\' file in \'{knownwikis.dirs[0]}\' and \'{knownwikis.dirs[1]}\'
Github: 🌐{Colors.blue_underline}{__url__}{Colors.reset}
Request to add new wiki: 🌐{Colors.blue_underline}{__newwikirequesturl__}{Colors.reset}''',
        formatter_class = argparse.RawTextHelpFormatter,
    )
    parser.add_argument('-w', '--wiki', default='archwiki',
                         help='Load a known wiki by name (ex: --wiki=wikipedia) [Default: archwiki]',
                         choices=knownwikis.getnames())
    parser.add_argument('-u', '--url', default=None,
                         help='URL of wiki to browse (ex: https://fr.wikipedia.org, https://wiki.freebsd.org)')
    parser.add_argument('-s', '--searchstring', default=None,
                         help='alternative search string (ex: \"/wiki/Special:Search?go=Go&search=\", \"/FrontPage?action=fullsearch&value=\")')
    parser.add_argument('-c', '--conv', default=None,
                        choices=['raw', 'clean', 'basic', 'md', 'txt'],
                        help='''conversion mode:
raw: no conversion (but still remove binaries)
clean: convert to cleaner HTML (remove styles and scripts)
basic: convert to basic HTML
md: convert to markdown
txt: convert to plain text
[Default: \'raw\' in graphical environment, \'basic\' otherwise]''',)
    parser.add_argument('--offline', '--test', default=False, action='store_true',
                         help='Don\'t try to go online, only use cached copy if it exists')
    parser.add_argument('--refresh', default=False, action='store_true',
                        help='Force going online and refresh the cache')
    parser.add_argument('-v', '--version', default=False, action='store_true',
                        help='Print version number and exit')
    parser.add_argument('-x', '--export', default=False, action='store_true',
                        help='Export cache as .zip file')
    parser.add_argument('-m', '--merge', default=None,
                        help='Import and merge cache from a zip file created with --export') #TODO validate the import
    parser.add_argument('-ni', '--noicon', default=False, action='store_true',
                         help=f'Don\'t show the {__icon__} notification area icon - only <ctrl+c> will stop')
    parser.add_argument('--clear', default=False, action='store_true',
                        help='Clear cache and exit')
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    parser.add_argument('search', help='string to search (ex: \"installation guide\")', nargs='?',
                        const=None, type=str)
    
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            msg = f'Could not parse {e} arguments'
            __logger__.critical(msg)
            print(knownwikis.gethelpstring())
        sys.exit(e.code)

    if args.version:
        print(__version__)
        sys.exit(0)

    if not args.search:
        search = ''
    else:
        search = args.search

    if not args.conv:
        if 'DISPLAY' in os.environ:
            conv = 'raw'
        else:
            conv = 'basic'
    else:
        conv = args.conv

    core = Core(knownwikis,
                # alt_browser=args.browser,
                conv=conv,
                base_url=args.url, 
                search_parm=args.searchstring,
                offline=args.offline,
                refresh=args.refresh,
                debug=args.debug,
                wiki=args.wiki,
                noicon=args.noicon,
                )

    if (args.clear):
        asyncio.run(_clear(core))
        sys.exit(0)

    if (args.export):
        if (args.merge):
            __logger__.critical('--export and --merge can\'t be used together')
            sys.exit(-6)
        ZIP().export(core.proxy.cache_dir)
        sys.exit(0)

    if (args.merge):
        if args.export:
            __logger__.critical('--export and --merge can\'t be used together')
            sys.exit(-6)
        ZIP().merge(core.proxy.cache_dir, args.merge)
        sys.exit(0)

    try:
        asyncio.run(_main(core, search))
    except KeyboardInterrupt:
        pass #exception CancelledError will be caught in main

if __name__ == '__main__':
    main()
