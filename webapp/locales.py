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
    _data: dict = None

    def __init__(self, data: dict):
        object.__setattr__(self, '_data', data)

    def __setattr__(self, option, value) -> None:
        self._data[option] = value

    def __getattr__(self, option: str) -> str:
        option = option.replace('_', '-')
        return self._data.get(option)

    def get_data(self) -> dict:
        return self._data


_default_lang_obj = Lang


class Locales:
    def __init__(self, static_path, lang_class: None = Lang):
        self.source_path = static_path
        self._cache = {}
        self._lang_class = lang_class or _default_lang_obj

    def get_abspath(self, filename: str) -> str:
        return os.path.join(self.source_path, filename)

    def get_cache(self, filename: str):
        return self._cache[filename]

    def get_lang(self, filename) -> 'Lang':
        return self._lang_class(self.read(filename))

    def set_cache(self, filename: str, value: 'Lang') -> None:
        self._cache[filename] = value

    def validate_cache(self, filename):
        return filename in self._cache

    @staticmethod
    def read(filename):
        with open(filename) as fp:
            data = json.load(fp)
        return data

    def load(self, filename) -> 'Lang':
        filename = self.get_abspath(filename)
        if self.validate_cache(filename):
            return self.get_cache(filename)

        lang = self.get_lang(filename)
        self.set_cache(filename, lang)
        return lang


i18n = Locales(core.static_folder)


def load_available_languages(code_list):
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
