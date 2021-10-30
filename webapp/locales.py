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
import json
import os
from typing import List

from babel import Locale
from flask import request
from flask_babel import get_locale as get_flask_locale

from .settings import settings_pool as settings
from .webapp import babel
from .webapp import core


languages: List[Locale] = []


class Lang:
    """
    Class used for a translation of a specific language.

    This class has a special feature, which allows you to obtain the values
    through python code, although this implies some limitations, such as the
    impossibility of using integers at the beginning of the name for
    attributes/variables.

    :param data: A ``dict`` object with the translations.

    Example usage::

        >>> lang = Lang({'unique-key': 'awesome value'})
        >>> lang.unique_key
        'awesome value'
        >>>
    """
    _data: dict = None

    def __init__(self, data: dict):
        """
        Initialize the object.
        """
        object.__setattr__(self, '_data', data)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.get_data())

    def __setattr__(self, option, value) -> None:
        self._data[option] = value

    def __getattr__(self, option: str) -> str:
        option = option.replace('_', '-')
        return self._data.get(option)

    def get_data(self) -> dict:
        """
        Returns the dictionary with the translations.

        :return: A ``dict`` with the translations
        """
        return self._data


_default_lang_obj = Lang


class Locales:
    """
    Load translations from JSON files in a directory. When a file is loaded,
    it is cached to be available for query.

    :param static_folder: The folder where the translations are located.
    :param lang_class: Class from which the objects with the translations
        will be created, the default value is ``Lang``.

    Example usage::

        >>> locales = Locales('/static/locales/')
        >>> locales.load('page/es.json')
        Lang({'unique-key': 'awesome value'})
        >>> abspath = locales.get_abspath('page/es.json')
        >>> abspath
        '/static/locales/page/es.json'
        >>> locales.validate_cache(abspath)
        True
        >>>
    """
    def __init__(self, static_folder: str, lang_class: None = Lang):
        self.source_path = static_folder
        self._cache = {}
        self._lang_class = lang_class or _default_lang_obj

    def get_abspath(self, filename: str) -> str:
        """
        Returns the absolute path of a file.

        :param filename: A string with the location of the file
        :return: Absolute path
        """
        return os.path.join(self.source_path, filename)

    def get_cache(self, filename: str):
        """
        Returns a ``Lang`` object from the cache (if exists).

        :param filename: File name for the translation.
        :return: A ``Lang`` object
        """
        return self._cache[filename]

    def get_lang(self, filename) -> 'Lang':
        """
        Read and load a translation from a JSON file, and return it as a
        ``Lang`` object.

        :param filename: Location for the JSON file.
        :return: A ``Lang`` object.
        """
        return self._lang_class(self.read(filename))

    def set_cache(self, filename: str, value: 'Lang') -> None:
        """
        Add a translation to the cache.

        :param filename: Translation file location.
        :param value: Translation object to be cached.
        """
        self._cache[filename] = value

    def validate_cache(self, filename: str) -> bool:
        """
        Check if a translation is cached.

        :return: Returns ``True`` if is cached, otherwise, returns ``False``
        """
        return filename in self._cache

    @staticmethod
    def read(filename: str) -> dict:
        """
        Read and load a translation from a JSON file, and return it as a
        ``dict`` object.

        :param filename: Relative path for the JSON file.
        :return: A ``dict`` object.
        """
        with open(filename) as fp:
            data = json.load(fp)
        return data

    def load(self, filename: str) -> 'Lang':
        """
        Read and load a translation, and return it as a ``Lang`` object.

        This method is like get_lang, Except it has the cache feature.
        if the filename is in cache, the disk read is skipped and the stored
        object is returned, otherwise, it is read from disk, cached, and the
        result is returned.

        :param filename: Relative path for the JSON file.
        :return: A ``Lang`` object.
        """
        filename = self.get_abspath(filename)
        if self.validate_cache(filename):
            return self.get_cache(filename)

        lang = self.get_lang(filename)
        self.set_cache(filename, lang)
        return lang


i18n = Locales(core.static_folder)


def load_available_languages(code_list: str):
    for code in code_list.split(','):
        languages.append(Locale(code))


@core.context_processor
def ctx_languages():
    return dict(available_languages=languages, get_locale=get_flask_locale)


@babel.localeselector
def get_locale() -> Locale:
    a_lang = [lang.language for lang in languages]
    source = [request.args, request.cookies]
    # LOCALE: BY USER
    #################
    for src in source:
        locale = src.get('locale', None)
        if locale is None or locale not in a_lang:
            continue
        return Locale(locale)

    # LOCALE: BY SERVER
    ###################
    if request.accept_languages is None or len(request.accept_languages) == 0:
        return Locale(settings.locales.language)
    return Locale(request.accept_languages.best_match(a_lang))
