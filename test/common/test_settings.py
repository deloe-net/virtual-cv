import binascii
import unittest
from unittest import mock

from webapp import settings
from webapp.exceptions import CriticalError
from webapp.settings import EnvironEngine
from webapp.settings import ParserProxy
from webapp.settings import Secrets
from webapp.settings import SectionProxy
from webapp.settings import VaultEngine


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


class TestSecrets(unittest.TestCase):
    def test_secret_create(self):
        s = Secrets()
        self.assertIs(s.engine, None)

    @mock.patch('ast.literal_eval', clear=True)
    def test_secret_converter_literal(self, literal_mock):
        s = Secrets()
        s.converter('value', to_python=True)
        literal_mock.assert_called_once_with('value')

    @mock.patch('ast.literal_eval', clear=True)
    def test_secret_converter_type(self, literal_mock):
        s = Secrets()
        d = mock.MagicMock()
        s.converter('value', data_type=d)
        d.assert_called_once_with('value')
        literal_mock.assert_not_called()

    @mock.patch('ast.literal_eval', clear=True)
    def test_secret_converter_no_kwargs(self, literal_mock):
        s = Secrets()
        self.assertEqual(s.converter('value'), 'value')
        literal_mock.assert_not_called()

    def test_secret_to_unicode(self):
        s = Secrets()
        v = mock.MagicMock(spec=bytes)
        v.decode.return_value = 'value'
        s.to_unicode(v)
        v.decode.assert_called_once_with(settings._default_encoding)

        v = mock.MagicMock(spec=str)
        v.decode = mock.MagicMock()
        v.decode.return_value = None
        self.assertIsInstance(s.to_unicode('value'), str)
        v.decode.assert_not_called()

    @mock.patch('base64.b64decode', clear=True)
    def test_secret_b64decode(self, b64_mock):
        s = Secrets()
        v = 'dGVzdA=='
        s.b64decode('name', v)
        b64_mock.assert_called_with(v)

        b64_mock.side_effect = binascii.Error()
        self.assertRaises(CriticalError, s.b64decode, 'name', v)
        b64_mock.assert_called_with(v)

    def test_secret_get_value_chk_engine(self):
        s = Secrets()
        self.assertRaisesRegex(
            CriticalError, 'No secret engine was provided.',
            s.get_value, 'test')

        s.engine = mock.MagicMock()
        s.engine.get_value.return_value = settings.DEFAULT_NULL_RANDOM
        k = 'test'
        self.assertRaisesRegex(
            CriticalError, 'not found: %s' % k,
            s.get_value, k)
        s.engine.get_value.assert_called_once_with(k)

    def test_secret_get_value_default(self):
        s = Secrets(mock.MagicMock())
        s.engine.get_value.return_value = settings.DEFAULT_NULL_RANDOM
        s.b64decode = mock.MagicMock()
        s.to_unicode = mock.MagicMock()
        s.converter = mock.MagicMock()
        self.assertEqual(s.get_value('test', default='default'), 'default')
        s.b64decode.assert_not_called()
        s.to_unicode.assert_not_called()
        s.converter.assert_not_called()

    def test_secret_get_value_no_kwargs(self):
        k = 'test_key'
        v = 'test_value'

        s = Secrets(mock.MagicMock())
        s.engine.get_value.return_value = v
        s.b64decode = mock.MagicMock()
        s.to_unicode = mock.MagicMock()
        s.converter = mock.MagicMock()
        s.converter.return_value = v
        self.assertEqual(s.get_value(k), v)
        s.b64decode.assert_not_called()
        s.to_unicode.assert_not_called()
        s.converter.assert_not_called()

    def test_secret_get_value_b64(self):
        k = 'test_key'
        e = 'encoded_value'
        d = 'decoded_value'
        s = Secrets(mock.MagicMock())
        s.engine.get_value.return_value = e
        s.b64decode = mock.MagicMock()
        s.b64decode.return_value = d
        s.to_unicode = mock.MagicMock()
        s.converter = mock.MagicMock()

        self.assertEqual(s.get_value(k, b64decode=True), d)
        s.b64decode.assert_called_once_with(k, e)
        s.to_unicode.assert_not_called()
        s.converter.assert_not_called()

    def test_secret_get_value_utf(self):
        k = 'test_key'
        b = b'no_utf_value'
        u = 'utf_value'
        s = Secrets(mock.MagicMock())
        s.engine.get_value.return_value = b
        s.b64decode = mock.MagicMock()
        s.to_unicode = mock.MagicMock()
        s.to_unicode.return_value = u
        s.converter = mock.MagicMock()

        self.assertEqual(s.get_value(k, unicode=True), u)
        s.b64decode.assert_not_called()
        s.to_unicode.assert_called_once_with(b)
        s.converter.assert_not_called()

    def test_secret_get_value_conv(self):
        k = 'test_key'
        v = 'test_value'

        s = Secrets(mock.MagicMock())
        s.engine.get_value.return_value = v
        s.b64decode = mock.MagicMock()
        s.to_unicode = mock.MagicMock()
        s.converter = mock.MagicMock()
        s.converter.return_value = v

        self.assertEqual(s.get_value(k, data_type=str), v)
        s.b64decode.assert_not_called()
        s.to_unicode.assert_not_called()
        s.converter.assert_called_with(v, data_type=str, to_python=False)

        self.assertEqual(s.get_value(k, to_python=True), v)
        s.b64decode.assert_not_called()
        s.to_unicode.assert_not_called()
        s.converter.assert_called_with(v, data_type=None, to_python=True)


class TestVaultEngine(unittest.TestCase):
    def test_vault_create(self):
        c = mock.MagicMock()
        m = {}
        e = VaultEngine(m, c)
        d = {'_VaultEngine__kv_map': m, '_VaultEngine__client': c,
             '_VaultEngine__mp': None}
        self.assertDictEqual(e.__dict__, d)

    def test_vault_get_value_null(self):
        m = mock.MagicMock()
        m.get.return_value = None
        c = mock.MagicMock()
        e = VaultEngine(m, c)
        k = 'test_key'
        self.assertEqual(e.get_value(k), settings.DEFAULT_NULL_RANDOM)
        m.get.assert_called_once_with(k)

    def test_vault_get_value(self):
        f = 'test/path'
        t = 'test_vault_key'
        r = 'an super secret'
        d = mock.MagicMock()
        d.get.return_value = r
        p = {'path': f, 'key': t}
        s = {'data': {'data': d}}
        k = 'test_alias_key'

        m = mock.MagicMock()
        m.get.return_value = p
        c = mock.MagicMock()
        c.secrets.kv.read_secret_version.return_value = s
        e = VaultEngine(m, c)

        self.assertEqual(e.get_value(k), r)
        m.get.assert_called_once_with(k)
        c.secrets.kv.read_secret_version.assert_called_once_with(
            path=f,
            mount_point=None)
        d.get.assert_called_once_with(t, settings.DEFAULT_NULL_RANDOM)

    def test_vault_get_value_err(self):
        f = 'test/path'
        t = 'test_vault_key'
        d = mock.MagicMock()
        p = {'path': f, 'key': t}
        s = {}
        k = 'test_alias_key'

        m = mock.MagicMock()
        m.get.return_value = p
        c = mock.MagicMock()
        c.secrets.kv.read_secret_version.return_value = s
        e = VaultEngine(m, c)
        self.assertEqual(e.get_value(k), settings.DEFAULT_NULL_RANDOM)
        m.get.assert_called_once_with(k)
        c.secrets.kv.read_secret_version.assert_called_once_with(
            path=f, mount_point=None)
        d.get.assert_not_called()


class TestEnvironEngine(unittest.TestCase):
    def test_environ_create(self):
        p = 'prefix'
        e = EnvironEngine(p)
        self.assertEqual(e.prefix, p)

    @mock.patch('os.environ', clear=True)
    def test_secret_get_value(self, environ):
        v = 'secret'
        p = 'PRE_'
        k = 'SECRET_VAR'
        f = p + k
        environ.get.return_value = v
        s = EnvironEngine(p)
        r = s.get_value(k)
        environ.pop.assert_not_called()
        environ.get.assert_called_once_with(f, settings.DEFAULT_NULL_RANDOM)
        self.assertEqual(r, v)

    @mock.patch('os.environ', clear=True)
    def test_secret_get_value_pop(self, environ):
        v = 'secret'
        p = 'PRE_'
        k = 'SECRET_VAR'
        f = p + k
        environ.pop.return_value = v
        s = EnvironEngine(p)
        r = s.get_value(k, pop=True)
        environ.get.assert_not_called()
        environ.pop.assert_called_once_with(f, settings.DEFAULT_NULL_RANDOM)
        self.assertEqual(r, v)


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


__all__ = ['TestBasicSettings', 'TestSecrets', 'TestVaultEngine',
           'TestEnvironEngine', 'TestSettingsPool']
