# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import yaml
try:
    from __init__ import __name__, __newwikirequesturl__, logger
except ModuleNotFoundError:
    from arch_wiki_search.arch_wiki_search import __name__, __newwikirequesturl__, logger
    
class Wiki:
    name = ''
    url = ''
    searchstring = ''

    def __init__(self, name, url, searchstring):
        self.name = name
        self.url = url
        self.searchstring = searchstring

    def __str__(self):
        return f'{self.name}: {Colors.blue_underline}{self.url}{Colors.reset} ({self.searchstring})'

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
        s += str(self)
        return s

    def __str__(self):
        s = ''
        for name in self.getnames():
            for wiki in self:
                if name == wiki.name:
                    s += f'- {wiki}\n'
                    break
        return s

    def __init__(self, filename='wikis.yaml', debug=False):
        self.filename = filename
        self.debug = debug
        super().__init__()

        # check where the python file of the loaded module is
        self.dirs.append(os.path.dirname(os.path.realpath(__file__)))

        # check in standard OS user config locations
        if os.name == 'posix': 
            configdir = os.path.join(os.path.expanduser('~'), '.config', __name__)
        elif os.name == 'nt': 
            configdir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', __name__)
        self.dirs.append(configdir)

        for d in self.dirs:
            path = d + '/' + self.filename
            try:
                f = open(path, 'r')
                try:
                    docs = yaml.safe_load_all(f)
                except Exception as e:
                    msg = f'Could not load yaml {path}: {e}'
                    logger.error(msg)
                    raise Exception(msg)
                for doc in docs:
                    try:
                        self.add(Wiki(doc['name'], doc['url'], doc['searchstring']))
                    except Exception as e:
                        logger.warning(f'Could not read entry {doc} from file {path}')
                f.close()
            except Exception as e:
                msg = f'Could not load known wikis file {path}: {e}'
                if (self.debug): print(msg)
                logger.debug(msg)
        if len(self) == 0:
            msg = 'No known wikis found'
            logger.error('No known wikis found')
            raise KeyError(msg)
        else:
            if (self.debug): logger.debug('Known wikis: ' + str(self))
        
