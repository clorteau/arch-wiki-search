
""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import tempfile
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
try:
    from __init__ import __logger__, __name__
except ModuleNotFoundError:
    from arch_wiki_search.arch_wiki_search import __logger__, __name__

class ZIP:
    """Read and write whole caches as ZIP files
    """
    def __init__(self):
        self.timestamp = '{:%Y%m%d_%H-%M-%S}'.format(datetime.now())
    
    def export(self, dir_path, out_path='.'):
        file_name = f'{out_path}/{__name__}-{self.timestamp}.zip'
        try:
            with ZipFile(file_name, 'w', ZIP_DEFLATED) as zfile:
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        zfile.write(os.path.join(root, file),
                                    os.path.relpath(os.path.join(root, file),
                                                    os.path.join(dir_path, '..')))
                __logger__.info(f'Export from \'{dir_path}\' to \'{file_name}\' successful')
        except Exception as e:
            msg = f'Failed creating export \'{file_name}\' from \'{dir_path}\':\n{e}'
            logger.critical(msg)
            raise e

    def merge(self, dir_path, inzip):
        try:
            with ZipFile(inzip, 'r') as zfile:
                zfile.extractall(dir_path) #TODO: validate import
            __logger__.info(f'Import from {inzip} to {dir_path} successful')
        except Exception as e:
            msg = f'Failed import to {dir_path} from {inzip}:\n{e}'
            __logger__.critical(msg)

class StopFlag:
    """A boolean stored as a temp file that will be updated by the QT GUI to tell the proxy to stop
    """
    filePath = None

    def write(self, b):
        assert (b == True or b == False)
        with open(self.filePath, 'w') as temp_file:
            temp_file.write(str(b))
            self.filePath = temp_file.name

    def read(self) -> bool:
        if self.filePath == None: return False
        if not os.path.exists(self.filePath): return False
        try:
            with open(self.filePath, 'r') as temp_file:
                s = temp_file.read()
                b = True if s.lower() == 'true' else False
            return b
        except Exception as e:
            msg = f'Could not read temp file {self.filePath}: {e}'
            __logger__.warning(msg)

    def delete(self):
        if (self.filePath != None):
            try:
                os.remove(self.filePath)
            except Exception as e:
                msg = f'Could not delete temp file {self.filePath}: {e}' #might block all future starts if not delted
                __logger__.error(msg)

    def __init__(self):
        self.filePath = os.path.join(tempfile.gettempdir(), f'{__name__}.stopflag')
        #to not block starts if flag remained and set to True
        if os.path.exists(self.filePath):
            self.delete()
        else:
            self.write(False)
