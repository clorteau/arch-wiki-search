
""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

# try:
#     from __init__ import __name__, logger
# except ModuleNotFoundError:
#     from arch_wiki_search.arch_wiki_search import __name__

class ZIP:
    def __init__(self):
        self.timestamp = '{:%Y%m%d_%H-%M-%S}'.format(datetime.now())
    
    def export(self, dir_path, out_path='.'):
        file_name = f'{out_path}/{__name__}-{self.timestamp}.zip'
        # if not dir_path.endswith('/'):
        #     dir_path += '/' #don't create a top level directory
        try:
            with ZipFile(file_name, 'w', ZIP_DEFLATED) as zfile:
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        zfile.write(os.path.join(root, file),
                                    os.path.relpath(os.path.join(root, file),
                                                    os.path.join(dir_path, '..')))
                logger.info(f'Export from \'{dir_path}\' to \'{file_name}\' successful')
        except Exception as e:
            msg = f'Failed creating export \'{file_name}\' from \'{dir_path}\':\n{e}'
            logger.critical(msg)
            raise e

    def merge(self, dir_path, inzip):
        try:
            with ZipFile(inzip, 'r') as zfile:
                zfile.extractall(dir_path) #TODO: validate import
            logger.info(f'Import from {inzip} to {dir_path} successful')
        except Exception as e:
            msg = f'Failed import to {dir_path} from {inzip}:\n{e}'
            logger.critical(msg)