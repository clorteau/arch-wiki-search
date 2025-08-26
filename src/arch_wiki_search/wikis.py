# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import yaml
try:
    from __init__ import __name__, __newwikirequesturl__, logger, Colors
except ModuleNotFoundError:
    from arch_wiki_search.arch_wiki_search import __name__, __newwikirequesturl__, logger, Colors
    
class Wiki:
    name = ''
    url = ''
    searchstring = ''

    def __init__(self, name, url, searchstring):
        self.name = name
        self.url = url
        self.searchstring = searchstring

class Wikis(set):
    filename = ''
    dirs = []

    def getnames(self):
        names = []
        for i, w in enumerate(self):
            names.append(w.name)
        return sorted(names)

    def gethelpstring(self):
        s = f'Known wikis are loaded from {Colors.yellow}{self.filename}{Colors.reset} files in these directories:\n'
        for d in self.dirs:
            s += f'🡪 {Colors.yellow}{d}{Colors.reset}\n'
        s += f'You can edit these files to add your own. If you do, please share at 🌐{Colors.blue_underline}{__newwikirequesturl__}{Colors.reset}\n'
        s += f'The currently known wikis are:\n'
        for name in self.getnames():
            for wiki in self:
                if name == wiki.name:
                    s += f'- {wiki.name}: {wiki.url}\n'
                    break
        return s

    def __init__(self, filename='wikis.yaml'):
        self.filename = filename
        super().__init__()
        self.dirs.append(os.path.dirname(os.path.realpath(__file__)))
        if os.name == 'posix': 
            configdir = os.path.join(os.path.expanduser('~'), '.config', __name__)
        elif os.name == 'nt': 
            configdir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', __name__)
        self.dirs.append(configdir)
        for d in self.dirs:
            path = d + '/' + self.filename
            try:
                f = open(path, 'r')
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    try:
                        self.add(Wiki(doc['name'], doc['url'], doc['searchstring']))
                    except Exception as e:
                        logger.debug(f'Could not add {doc}')
                f.close()
            except Exception as e:
                logger.debug(f'Could not load known wikis file {path}: {e}')
        if len(self) == 0:
            msg = 'No known wikis found'
            logger.error('No known wikis found')
            raise KeyError(msg)
        else:
            logger.debug('Known wikis: ' + str(self))
        
