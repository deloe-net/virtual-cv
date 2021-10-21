import base64
import os
import unittest
from unittest import mock

from webapp.exceptions import CriticalError
from webapp.settings import ParserProxy
from webapp.settings import Secrets
from webapp.settings import SectionProxy


class TestBasicSettings(unittest.TestCase):
    def test_basic_create(self):
        section = 'unittest'
        cfg = mock.MagicMock()
        s = SectionProxy(cfg, section)
        self.assertEqual(s._section, section)
        self.assertIs(s._cp, cfg)

    def test_basic_integrity_class(self):
        self.assertIsNone(SectionProxy._section)
        self.assertIsNone(SectionProxy._cp)

    def test_basic_magic_getattr_to_python(self):
        t = 'unittest'
        c = mock.Mock()
        c.get.return_value = '101'
        s = SectionProxy(c, t)
        r = s.__getattr__('mocked_attr')
        s._cp.get.assert_called_with(t, 'mocked_attr')
        self.assertEqual(r, 101)

    def test_basic_magic_getattr_no_python(self):
        t = 'unittest'
        v = '1*1'
        c = mock.Mock()
        c.get.return_value = v
        s = SectionProxy(c, t)
        r = s.__getattr__('mocked_attr')
        s._cp.get.assert_called_with(t, 'mocked_attr')
        self.assertEqual(v, r)

    def test_basic_magic_setattr(self):
        t = 'unittest'
        v = '1*1'
        c = mock.Mock()
        s = SectionProxy(c, t)
        self.assertIsNone(s.__setattr__('mocked_attr', v))
        s._cp.set.assert_called_with(t, 'mocked_attr', v)


class TestSecretSettings(unittest.TestCase):
    def test_secret_create(self):
        s = Secrets('prefix')
        self.assertEqual(s.prefix, 'prefix')

    def test_secret_converter(self):
        s = Secrets('prefix')
        self.assertEqual(s.converter('intact'), 'intact')
        self.assertEqual(s.converter('1000', to_python=True), 1000)
        self.assertIs(s.converter('1', data_type=bool), True)

    def test_secret_decode(self):
        s = Secrets('prefix')
        c = base64.b64encode(b'test')
        self.assertIsInstance(s._decode(c), str)
        self.assertIsInstance(s._decode(c, unicode=None), bytes)

    def test_secret_catch_decode(self):
        s = Secrets('prefix')
        n = 'test'
        self.assertRaisesRegex(
            CriticalError, 'the secret value %s is in base64 format?' % n,
            s.decode, n, 'no base64')
        self.assertRaisesRegex(
            CriticalError, 'secret value of %s must be in base64' % n,
            s.decode, n, 'secret no base64')
        self.assertEqual(s.decode(n, base64.b64encode(b'test')), 'test')

    @mock.patch.dict(os.environ, {'PRE_SECRET_VAR': 'c2VjcmV0'}, clear=True)
    def test_secret_get_value(self):
        v = 'secret'
        c = 'utf-8'
        e = base64.b64encode(bytes(v, c)).decode(c)
        p = 'PRE_'
        n = 'SECRET_VAR'
        s = Secrets(p)
        s.decode = mock.MagicMock(return_value=v)
        s.converter = mock.MagicMock(return_value=v)
        s.get_value(name=n)
        s.decode.assert_called_once_with(p + n, e, unicode=True)
        s.converter.assert_called_once_with(v)

    @mock.patch.dict(os.environ, {'PRE_SECRET_VAR': 'c2VjcmV0'}, clear=True)
    def test_secret_get_value_pop(self):
        v = 'secret'
        c = 'utf-8'
        e = base64.b64encode(bytes(v, c)).decode(c)
        p = 'PRE_'
        n = 'SECRET_VAR'
        s = Secrets(p)
        s.decode = mock.MagicMock(return_value=v)
        s.converter = mock.MagicMock(return_value=v)
        s.get_value(name=n, pop=True)
        s.decode.assert_called_once_with(p + n, e, unicode=True)
        s.converter.assert_called_once_with(v)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_secret_get_value_default(self):
        v = 'never encode never decode'
        p = 'PRE_'
        n = 'SECRET_VAR'
        s = Secrets(p)
        s.decode = mock.MagicMock()
        s.converter = mock.MagicMock(return_value=v)
        self.assertEqual(s.get_value(name=n, default=v), v)
        s.decode.assert_not_called()
        s.converter.assert_called_once_with(v)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_secret_get_value_not_found(self):
        p = 'PRE_'
        n = 'SECRET_VAR'
        s = Secrets(p)
        s.decode = mock.MagicMock()
        s.converter = mock.MagicMock()
        self.assertRaisesRegex(
            CriticalError, 'secret value %s not found' % (p + n),
            s.get_value, n)
        s.decode.assert_not_called()
        s.converter.assert_not_called()


class TestSettingsPool(unittest.TestCase):
    def test_pool_create(self):
        cfg = mock.MagicMock()
        s = ParserProxy(cfg)
        self.assertIs(s._cp, cfg)
        self.assertIsInstance(s._sections, dict)
        self.assertDictEqual(s._sections, {})

    @mock.patch('webapp.settings._default_section_proxy', clear=True)
    def test_pool_magic_getattr(self, s_m):
        c = mock.Mock()
        s = ParserProxy(c)
        a = 'mocked_attr'
        s.__getattr__(a)
        self.assertIn(a, s._sections)
        s_m.assert_called_with(c, a)


__all__ = ['TestBasicSettings', 'TestSecretSettings', 'TestSettingsPool']
