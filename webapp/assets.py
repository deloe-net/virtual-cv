#  Copyright 2021 Ismael Lugo <ismael.lugo@deloe.net>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import base64
import hashlib
import os
import re
import shutil
import sys

from .common import Reactor
from .settings import get_secret
from .settings import settings_pool
from .webapp import core


cfg = settings_pool.security
hash_stack = {}


class Assets:
    """
    Create safe file names, making it more hard to map static files like style
    sheets, javascript files, etc.

    :param algm: Name of the hash algorithm, used to secure the files.
    :param salt: Unique and secret key used to secure files.

    """
    STATIC_FOLDER = core.static_folder
    REGEX_REPLACE = re.compile('[^a-zA-Z]')
    FILE_FORMATTER = '{basename}.{hashsum}{ext}'

    def __init__(self, algm: str, salt: bytes = None):
        """
        Initialize the object.
        """

        self.__salt = salt
        self._algm = algm
        self.__cache = {}

    @property
    def static_folder(self):
        return self.STATIC_FOLDER

    @property
    def file_formatter(self):
        return self.FILE_FORMATTER

    @property
    def regex_replace(self):
        return self.REGEX_REPLACE

    def update_salt(self, salt: bytes) -> None:
        """
        Update the unique key used to secure the files.

        :param salt: Unique and secret key used to secure files.
        """
        if isinstance(salt, str):
            salt = bytes(salt, 'utf-8')
        self.__salt = salt

    def get_abspath(self, filename: str) -> str:
        """
        Returns the absolute path of a file in the static folder.

        :param filename: Relative path of the file in the folder
        :return: Returns the absolute path of the file
        """
        return os.path.join(self.static_folder, filename)

    def format(self, **kwargs):
        """
        Create safe filenames according to file format.

        :param kwargs: The keyword arguments are passed to the str.format()
            method, the available arguments are::

            - basename: Base filename
            - hashsum: File hash identifier
            - ext: Extension used in the file

        :return: returns the end name of the secured file
        """
        return self.file_formatter.format(**kwargs)

    def digest(self, data: bytes):
        """
        Generate the hash identifier from the supplied data.

        :param data: supplied data to generate the hash identifier
        :return: returns the generated hash identifier
        """
        hashsum = hashlib.pbkdf2_hmac(self._algm, data, self.__salt, 1000)
        hashsum = base64.b64encode(hashsum)
        if isinstance(hashsum, bytes):
            hashsum = hashsum.decode('utf8')
        return self.regex_replace.sub('', hashsum)

    def get_file_hash(self, filename: str):
        """
        Generates a hash identifier from the name of a supplied file.

        :param filename: File name to generate the hash identifier
        :return: returns the generated hash identifier
        """
        return self.digest(bytes(filename, 'utf-8'))

    def secure_filename(self, filename: str):
        """
        Returns the secure name for a file according to the path. This method
        has the feature that in case the file name has been previously
        processed, it verifies that it is available in the cache memory. If
        found, the value is returned from cache, otherwise, it is processed,
        and added to the cache.

        :param filename: path where the file is located
        :return: returns the safe filename.
        """

        if filename in self.__cache:
            hashsum = self.__cache[filename]
        else:
            hashsum = self.__cache[filename] = self.get_file_hash(filename)

        dirname = os.path.dirname(filename)
        fn_parts = os.path.splitext(os.path.basename(filename))
        filename = self.format(basename=fn_parts[0],
                               hashsum=hashsum,
                               ext=fn_parts[1])
        return os.path.join(dirname, filename)


assets = Assets('sha256', salt=b'')


# ASSETS CLI
###############################################################################
class AssetsCLI(Reactor):
    def __init__(self, parent):
        self.name = 'assets'
        self.parser = parent.add_parser(self.name, help='Actions in Assets')

        self.parser.add_argument('-s', '--secure', action='store_true')
        self.parser.add_argument(
            '-f', '--from-file',
            dest='filename',
            metavar=('filename',),
            required=True
        )
        self.parser.add_argument('--simulate', action='store_true')
        self.parser.add_argument('--salt', metavar='TEXT', type=str)

    @staticmethod
    def secure(filename: str, simulate: bool = True):
        abspath = assets.get_abspath(filename)
        if not os.path.exists(abspath):
            print('file not found: %s', filename, file=sys.stderr)
            exit(1)
        dst = assets.secure_filename(filename)
        if not simulate:
            shutil.move(assets.get_abspath(filename), assets.get_abspath(dst))
        print(f'rename: {filename}  ->  {dst}',  file=sys.stderr)

    def secure_by_list(self, file_list: str, **kwargs):
        with open(file_list) as fp:
            data = fp.read().splitlines()
        for filename in data:
            self.secure(filename, **kwargs)

    def process(self, args):
        if args.salt:
            salt = args.salt
        else:
            salt = get_secret('ASSETS_SALT')

        assets.update_salt(salt)
        if args.secure:
            self.secure_by_list(args.filename, simulate=args.simulate)
        else:
            self.parser.print_help()


def sf(filename: str):
    if settings_pool.server.debug_mode:
        return filename
    return assets.secure_filename(filename)


@core.context_processor
def ctx_sf():
    return dict(sf=sf)
