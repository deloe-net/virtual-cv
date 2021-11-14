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
import re
import unittest
from unittest import mock

from webapp.assets import Assets
from webapp.webapp import core


class TestAssets(unittest.TestCase):
    def test_obj_create(self):
        a = Assets('sha256')
        assert a._salt is None
        assert a._algm == 'sha256'
        assert isinstance(a._cache, dict)

    def test_attr_sf(self):
        assert Assets.STATIC_FOLDER == core.static_folder

    def test_attr_regex(self):
        assert isinstance(Assets.REGEX_REPLACE, re.Pattern)

    def test_attr_fmt(self):
        assert isinstance(Assets.FILE_FORMATTER, str)
        fmt = Assets.FILE_FORMATTER.format(basename='a', hashsum='b', ext='.c')
        assert fmt == 'a.b.c'

    def test_update_salt(self):
        a = Assets('md5')
        assert a._salt is None
        a.update_salt(b'test')
        assert a._salt == b'test'

    def test_update_salt_bytes_conv(self):
        a = Assets('md5')
        assert a._salt is None
        a.update_salt('test')
        assert isinstance(a._salt, bytes)
        assert a._salt == b'test'

    @mock.patch('os.path.join', clear=True)
    def test_get_abspath(self, join):
        a = Assets('md5')
        a.get_abspath('file.txt')
        join.assert_called_once_with(a.STATIC_FOLDER, 'file.txt')

    def test_format(self):
        assert Assets.format(basename='a', hashsum='b', ext='.c') == 'a.b.c'


__all__ = ['TestAssets']
