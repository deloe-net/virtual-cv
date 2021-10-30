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


__all__ = ['TestLang']
