
""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import pickle
import tempfile
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
# try:
#     from __init__ import __logger__, PACKAGE_NAME
# except ModuleNotFoundError:
#     from arch_wiki_search.arch_wiki_search import __logger__, PACKAGE_NAME
# from run import __logger__, PACKAGE_NAME
from __init__ import __logger__, PACKAGE_NAME
import core

class ZIP:
    """Read and write whole caches as ZIP files
    """
    def __init__(self):
        self.timestamp = '{:%Y%m%d_%H-%M-%S}'.format(datetime.now())
    
    def export(self, dir_path, out_path='.'):
        file_name = f'{out_path}/{PACKAGE_NAME}-{self.timestamp}.zip'
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
    """A boolean stored as a temp file that will be updated by the UI to tell the proxy to stop
    """
    filePath = None

    def write(self, b: bool):
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
        self.filePath = os.path.join(tempfile.gettempdir(), f'{PACKAGE_NAME}.stopflag')
        #to not block starts if flag remained and set to True
        if os.path.exists(self.filePath):
            self.delete()
        else:
            self.write(False)    

class DATA:
    """Class that will be serialized to exchange between processes
    """
    wikiname = ''
    wikiurl = ''
    wikisearchstring = ''
    port = 0
    favicon = ''

    def serialize(self) -> bytes:
        b = pickle.dumps(self)
        return b

    @staticmethod
    def deserialize(b: bytes):
        data = pickle.loads(b)
        return data

class CoreDescriptorFile:
    """Info exposed by each running core for UIs to read from through a temp file
    TODO: make sure the file is in RAM for speed
    """
    path = ''
    path_pattern = ''
    data = None

    def __init__(self, port: int):
        # one file per core so UIs can show multiple wikis at once
        self.path = CoreDescriptorFile.get_path_pattern() + str(port)
        self.data = DATA()
        self.data.port = port

    @staticmethod
    def get_path_pattern():
        return os.path.join(tempfile.gettempdir(), f'{PACKAGE_NAME}.core.')

    def write_data(self):
        b = self.data.serialize()
        try:
            with open(self.path, 'wb') as f:
                f.write(b)
            __logger__.debug(f'Wrote core info temp file {self.path}')
        except Exception as e:
            msg = f'Failed to write core info to temp file {self.path}: {e}'
            __logger__.warning(msg)

    def read_data(self):
        try:
            with open(self.path, 'rb') as f:
                b = f.read()
                self.data = DATA.deserialize(b)
                __logger__.debug(f'Read from core info temp file {self.path}')
                return self.data
        except Exception as e:
            msg = f'Failed to read core info from temp file {self.path}: {e}'
            __logger__.warning(msg)

    def delete(self):
        if (self.path != None):
            try:
                os.remove(self.path)
            except Exception as e:
                msg = f'Could not delete temp file {self.path}: {e}'
                __logger__.warning(msg)

class SharedMemory:
    """Data exposed by Core for the UIs to read in shared memory across process boundaries
    Not used see FIXME
    """
    from multiprocessing import shared_memory

    _sharedmem = None
    name = f'{PACKAGE_NAME}.core'

    def __init__(self, create: bool):
        size = 1024 #1kB should be enough to store a few strings and an int
        # try:
        self._sharedmem = shared_memory.SharedMemory(name=self.name, create=create, size=size)
        self.data = DATA()

    def _serialize(self, data) -> bytes:
        b = pickle.dumps(data)
        __logger__.debug(f'Wrote {len(b)} bytes in shared memory')
        return b

    def _deserialize(self, b: bytes):
        data = pickle.loads(b)
        __logger__.debug(f'Read {len(b)} bytes from shared memory')
        return data

    def write_data(self) -> None:
        b = self._serialize(self.data) #bytes
        self._sharedmem.buf[:len(b)] = b

    def read_data(self):
        self.data = self._deserialize(self._sharedmem.buf)
        return self.data

    def close(self, delete: bool):
        assert self._sharedmem != None
        # FIXME: each process spawns a resource tracker that deletes the block when the process
        # closes  the handle, warning it had to do it, and the 2nd process with its own tracker
        # throws warnings that it needs to be deleted and then that it can't because
        # it was already deleted
        # https://bugs.python.org/issue38119
        # can't  even suppress warnings so using a temp file again
        # Doesn't work either:
        # from multiprocessing import resource_tracker
        # resource_tracker._resource_tracker._stop()
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            try:
                self._sharedmem.close()
            except Exception as e:
                    __logger__.warn(f'Failed to close shared memory block: {e}')
            if delete:
                try:
                    #self._sharedmem.close()
                    self._sharedmem.unlink()
                except Exception as e:
                    if e.args[0] == 2:
                        pass # err code 2 = not found so it was already deleted
                    else:
                        __logger__.warn(f'Failed to delete shared memory block: {e}')

