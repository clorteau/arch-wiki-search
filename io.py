
""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from __init__ import __name__, logger

class IO:
    @staticmethod
    def export(dir_path, out_path):
        file_name = '{:%Y%m%d_%H-%M-%S}.zip'.format(datetime.now())
        file_name += __name__

        with ZipFile(out_path, 'w', ZIP_DEFLATED) as zfile:
            for root, dirs, files in os.walk(root, file):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zfile.write(file_path, arcname)