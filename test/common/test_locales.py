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

    @mock.patch('os.path.join', clear=True)
    def test_get_abspath(self, join):
        p = '/test/absolute/path'
        n = 'relative/route'
        m = mock.MagicMock()
        o = Locales(p)
        join.return_value = m
        r = o.get_abspath(n)
        join.assert_called_once_with(p, n)
        assert r is m

    def test_get_cache(self):
        f = '/test/filename.json'
        t = mock.MagicMock()
        o = Locales('./')
        o._cache = mock.MagicMock(spec=dict)
        o._cache.__getitem__.return_value = t
        assert o.get_cache(f) is t
        o._cache.__getitem__.assert_called_once_with(f)

    def test_get_cache_undefined(self):
        f = '/test/filename.json'
        o = Locales('./')
        self.assertRaises(KeyError, o.get_cache, f)

    def test_set_cache(self):
        f = '/test/filename.json'
        t = mock.MagicMock()
        o = Locales('./')
        o._cache = mock.MagicMock(spec=dict)
        o.set_cache(f, t)
        o._cache.__setitem__.assert_called_once_with(f, t)

    def test_in_cache(self):
        f = '/test/filename.json'
        o = Locales('./')
        o._cache = mock.MagicMock(spec=dict)
        o._cache.__contains__.return_value = True
        self.assertTrue(o.validate_cache(f))
        o._cache.__contains__.assert_called_once_with(f)

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
    @mock.patch('json.load', clear=True)
    def test_read(self, json_load, mock_file):
        f = '/test/filename.json'
        d = {'mock-json': 'some-value'}
        json_load.return_value = d
        r = Locales.read(f)
        json_load.assert_called()
        mock_file.assert_called_with(f)
        self.assertDictEqual(r, d)

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
