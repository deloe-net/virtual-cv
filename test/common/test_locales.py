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
import os
import unittest
from unittest import mock

from webapp.locales import _default_lang_obj
from webapp.locales import Lang
from webapp.locales import Locales


class TestLang(unittest.TestCase):
    def test_obj_create(self):
        e = {}
        d = Lang(e)
        assert d._data is e

    def test_func_get_data(self):
        e = {}
        d = Lang(e)
        assert d.get_data() is e

    def test_magic_getattr(self):
        v = 'a unique value'
        m = mock.MagicMock()
        m.get.return_value = v
        d = Lang(m)
        r = d.__getattr__('option_name')
        m.get.assert_called_once_with('option-name')
        assert r == v

    def test_magic_setattr(self):
        v = 'a unique value'
        k = 'option-name'
        m = mock.MagicMock()
        d = Lang(m)
        d.__setattr__(k, v)
        m.__setitem__.assert_called_once_with(k, v)


class TestLocales(unittest.TestCase):
    def test_obj_create(self):
        p = './'
        o = Locales(p)
        assert o.source_path == p
        assert isinstance(o._cache, dict)
        assert o._lang_class is _default_lang_obj

        c = mock.MagicMock()
        o = Locales(p, c)
        assert o._lang_class is c

    def test_get_abspath(self):
        p = '/test/absolute/path'
        n = 'relative/route'
        o = Locales(p)
        r = o.get_abspath(n)
        assert r == os.path.join(p, n)
        assert os.path.isabs(r)

    def test_cache(self):
        o = Locales('./')
        k = 'test-key'
        v = mock.MagicMock()
        assert o.set_cache(k, v) is None
        assert o.validate_cache(k)
        assert o.get_cache(k) is v

    def test_pre_load(self):
        v = 'return-value'
        c = mock.MagicMock(return_value=v)
        r = {'unique-key': 'awesome value'}
        f = 'test-filename.txt'

        o = Locales('./', c)
        o.read = mock.MagicMock(return_value=r)
        assert o._load(f) == v
        o.read.assert_called_once_with(f)
        c.assert_called_once_with(r)

    @mock.patch('builtins.open',
                new_callable=mock.mock_open,
                read_data='{"mock-json": "some-value"}')
    def test_read(self, mock_file):
        f = '/test/filename.json'
        r = Locales.read(f)
        mock_file.assert_called_with(f)
        self.assertDictEqual(r, {'mock-json': 'some-value'})

    def test_load(self):
        v = 'unique-value-obj'
        p = '/test/path'
        f = 'lang-filename.json'
        d = os.path.join(p, f)
        m = mock.MagicMock()

        o = Locales(p, m)
        o.get_cache = mock.MagicMock()
        o.set_cache = mock.MagicMock()
        o._load = mock.MagicMock(return_value=v)
        r = o.load(f)
        o.get_cache.assert_not_called()
        o.set_cache.assert_called_once_with(d, v)
        assert r is v


__all__ = ['TestLang', 'TestLocales']
