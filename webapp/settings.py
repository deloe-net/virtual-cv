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
import abc
import ast
import base64
import glob
import os
import uuid
from binascii import Error as binasciiError
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from typing import Union

import hvac

from .exceptions import CriticalError
from .webapp import core

DEFAULT_NULL_RANDOM = uuid.uuid4().hex
_type_string = Union[bytes, str]
_default_encoding = 'utf-8'


class SectionProxy:
    """
    A proxy for a single section from a parser.

    It provides a basic layer to extend the use of ConfigParser in which
    it acts as a proxy, redirecting queries from the magic `__getattr__`
    and `__setattr__` methods to the corresponding methods in ConfigParser.

    As an additional feature when obtaining a value, it will try to convert
    safely to Python code.

    :param parser: a ConfigParser object
    :param section: section name to be redirected

    Example usage::

        >>> import configparser
        >>> cfg = configparser.ConfigParser()
        >>> cfg.add_section("test_section")
        >>> cfg.set("test_section", "test_option", "1")
        >>> # A query would typically be done with classical methods.
        >>> cfg.get("test_section", "test_option")
        '1'
        >>> # But it can be improved...
        >>> sec = SectionProxy(cfg, 'test_section')
        >>> sec.test_option
        1
        >>> sec.other_option = "test"
        >>> sec.other_option
        'test'
        >>>
    """

    _section: str = None
    _cp: ConfigParser = None

    def __init__(self, parser: ConfigParser, section: str) -> None:
        """
        Initialize the object.
        """

        object.__setattr__(self, '_cp', parser)
        object.__setattr__(self, '_section', section)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self._section}>'

    def __setattr__(self, option: str, value: any) -> None:
        self._cp.set(self._section, option, value)

    def __getattr__(self, option: str) -> any:
        value = self._cp.get(self._section, option)
        try:
            return ast.literal_eval(value)
        except ValueError:
            return value


_default_section_proxy = SectionProxy


class ParserProxy:
    """
    A proxy for a single section from a parser.

    It provides a basic layer to extend the use of ConfigParser in which
    it acts as a proxy, redirecting queries from the magic `__getattr__`
    to an SectionProxy object.

    Example usage::

        >>> import configparser
        >>> cfg = configparser.ConfigParser()
        >>>
        >>> sec = ParserProxy(cfg)
        >>> sec.test_section
        <SectionProxy: test_section>
        >>>
    """

    _cp = None
    _sections = None

    def __init__(self, parser: ConfigParser) -> None:
        """
        Initialize the object.

        :param parser: a ConfigParser object
        """
        self._cp = parser
        self._sections = {}

    def __getattr__(self, section: str) -> _default_section_proxy:
        if section in self._sections:
            return self._sections[section]

        self._sections[section] = _default_section_proxy(self._cp, section)
        return self._sections[section]


class SecretEngine(abc.ABC):
    """
    Abstract class where secret engines come from.
    """

    @abc.abstractmethod
    def get_value(self, *args, **kwargs):
        pass


class VaultEngine(SecretEngine):
    """
    This is a secret engine that uses the hashicorp vault api.

    To correctly instantiate this class, you must provide a key/value map
    which should be governed by the following format::

        >>> kv_map = {
        ...     "VARIABLE-NAME": {"path": "vault-path", "key": "vault-key"}
        ... }

    :param kv_map: A ``dict`` object that contains the key/value map
        required to search for secrets.
    :param client: The hvac Client object for HashiCorp’s Vault.

    Example usage::

        >>> vault = hvac.Client(url='https://localhost:8200')
        >>> engine = VaultEngine(kv_map, vault)
    """

    def __init__(self, kv_map: dict, client: hvac.Client):
        """
        Initialize the object.
        """
        self.__kv_map = kv_map
        self.__client = client

    def get_value(self, key: str) -> str:
        """
        Return a secret according to the supplied key. If the value is not
        found or an error occurs during its processing, it returns by default
        ``DEFAULT_NULL_RANDOM``

        :param key: A string with the key used to find the secret.
        :return: The super secret value

        Example usage::

            >>> kv_map = {
            ...     "VARIABLE-NAME": {"path": "vault-path", "key": "vault-key"}
            ... }
            >>> vault = hvac.Client(url='https://localhost:8200')
            >>> engine = VaultEngine(kv_map, vault)
            >>> engine.get_value('VARIABLE-NAME')
            'super secret value'
            >>> engine.get_value('UNDEFINED-VARIABLE')
            '94273ec02822421e8bb9c7f7e2b12ad4'  # This is DEFAULT_NULL_RANDOM
        """
        kv = self.__kv_map.get(key)
        if kv is None:
            return DEFAULT_NULL_RANDOM

        res = self.__client.secrets.kv.read_secret_version(path=kv['path'])
        if 'data' in res:
            return res['data'].get(kv['key'], DEFAULT_NULL_RANDOM)
        else:
            return DEFAULT_NULL_RANDOM


class EnvironEngine(SecretEngine):
    """
    Manage secret data loaded in environment variables.

    :param prefix: string that indicates the prefix by starting the names
        of the environment variables.

    Attributes:
        prefix: prefix used by environment variables
    """

    def __init__(self, prefix: str):
        """
        Initialize the object.
        """
        self.prefix: str = prefix

    def get_value(self, key: str, pop: bool = False):
        """
        Read the environment variable and return its secret value. If the
        environment variable is not found, default is returned if given,
        otherwise CriticalError is raised.

        :param key: environment variable name.
        :param pop: remove the specific environment variable and return the
        corresponding value
        :return: The result in a string or bytes object.
        """
        name = self.prefix + key
        if pop:
            value = os.environ.pop(name, DEFAULT_NULL_RANDOM)
        else:
            value = os.environ.get(name, DEFAULT_NULL_RANDOM)
        return value


class Secrets:
    def __init__(self, engine: SecretEngine = None) -> None:
        self.engine = engine

    @staticmethod
    def converter(string: str,
                  data_type: type = None,
                  to_python: bool = False):
        """
        Try to convert a string to a data type usable by Python. When the
        data_type parameter is used, the data type to be converted must be
        specified, like as str or int, otherwise, if the to_python parameter
        is used, it will try to guess the data type, the latter is recommended
        for complex values. If no parameter is specified, the string will be
        returned without any modification.

        If both parameters, to_python and data_type are specified, only
        to_python will be executed, this is because the to_python parameter
        takes precedence during execution.

        :param string: text to be converted
        :param data_type: Type of data to be converted. Eg.: int, float, etc.
        :param to_python: Boolean value indicating to convert dynamically.
        :return: the converted value (if done).
        """

        if to_python:
            return ast.literal_eval(string)
        elif data_type is not None:
            return data_type(string)
        return string

    @staticmethod
    def to_unicode(text) -> str:
        """
        Convert a text (usually in bytes or ASCII) to unicode encoding.

        :param text: A text object to be converted
        :return: A str object in unicode
        """
        if isinstance(text, bytes):
            text = text.decode(_default_encoding)
        return text

    @staticmethod
    def b64decode(name: str, value: any) -> _type_string:
        """
        Decode the Base64 encoded bytes-like object or ASCII string.

        :param name: environment variable name
        :param value: str or bytes object encoded in base64 format

        :return: The result in a string or bytes object.
        :raises CriticalError: When some problem occurs during decoding
        """

        try:
            value = base64.b64decode(value)
        except (TypeError, binasciiError) as e:
            err_msg = 'secret value of %s must be in base64' % name
            raise CriticalError(err_msg) from e
        return value

    def get_value(self,
                  key: str,
                  default: any = DEFAULT_NULL_RANDOM,
                  b64decode: bool = False,
                  unicode: bool = False,
                  data_type: type = None,
                  to_python: bool = False,
                  **kwargs) -> _type_string:
        """
        Read the variable from the engine and return its secret value. If the
        environment variable is not found, default is returned if given,
        otherwise CriticalError is raised.

        :param key: variable name.
        :param default: Default value to return if the variable is not found.
        :param b64decode: Indicates that the result value must be decoded.
        :param unicode: Boolean value that indicates whether an object should
                be converted from bytes to unicode. The default value is False
        :param data_type: datatype to be converted the result. Eg.: int, etc.
        :param to_python: Boolean value indicating that the result should be
               evaluated as literal.
        :param kwargs: Keyword argument parameters are passed to the engine
               in use. For more information on the available parameters, see
               the help of the engine in use.

        :return: The result in a string or bytes object.
        :raises CriticalError: When the secret is not found or the engine
            has not been defined.
        """
        if self.engine is None:
            raise CriticalError('No secret engine was provided.')

        value = self.engine.get_value(key, **kwargs)
        if value == DEFAULT_NULL_RANDOM:
            if default != DEFAULT_NULL_RANDOM:
                return default
            raise CriticalError('not found: %s' % key)
        if b64decode:
            value = self.b64decode(key, value)
        if unicode:
            value = self.to_unicode(value)
        if data_type or to_python:
            value = self.converter(value,
                                   data_type=data_type,
                                   to_python=to_python)
        return value


_default_parser_proxy = ParserProxy
_global_secrets = Secrets()
_global_config = ConfigParser(interpolation=ExtendedInterpolation())
settings_pool = _default_parser_proxy(_global_config)


def set_secret_engine(engine: SecretEngine):
    _global_secrets.engine = engine


def get_secret(key: str, **kwargs):
    """
    Read the environment variable and return its secret value.
    If the environment variable is not found, default is returned if given,
    otherwise CriticalError is raised.

    :param key: environment variable name
    :param kwargs: For more information, see the help of Secrets.get_value(..)

    :return: The result in a string or bytes object.
    :raises CriticalError: When some problem occurs during decoding.
    """
    return _global_secrets.get_value(key, **kwargs)


def load(filename: str) -> None:
    """
    Read and parse a filename.

    :param filename: A string with the filename to be read.
    """
    with open(filename) as fp:
        _global_config.read_file(fp)


def load_dir(dir_path: str, ext='.cfg'):
    """
    Read and parse all files that contain the specified extension.

    :param dir_path: A string with the directory to check
    :param ext: Extension name, the default value is ".cfg"
    """
    filenames = glob.glob(os.path.join(dir_path, '*' + ext))
    _global_config.read(filenames)


@core.context_processor
def ctx_settings():
    return dict(settings=settings_pool)


__all__ = ['settings_pool', 'get_secret', 'load_dir', 'ParserProxy',
           'SectionProxy', 'Secrets', 'SecretEngine', 'VaultEngine',
           'EnvironEngine']
