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

from flask import Blueprint
from flask import render_template
from flask_babel import get_locale

from webapp.assets import sf
from webapp.blueprint.auth.backend.security.tools import access_token_needed
from webapp.locales import i18n

bp_frontend_home = Blueprint('frontend_home', __name__, url_prefix='/')

regex = {
    'skills': re.compile(r'^skill-(?P<n>\d{1,2})$'),
    'edu': re.compile(r'^(?P<n>\d{1,2})-edu-degree$'),
    'wxp': re.compile(r'^(?P<n>\d{1,2})-w-xp-comp$'),
    'vxp': re.compile(r'^(?P<n>\d{1,2})-v-xp-comp$'),
    'crt': re.compile(r'^(?P<n>\d{1,2})-crt-img$'),
}


@bp_frontend_home.context_processor
def ctx_home():
    i18n_data = i18n.load(sf('locales/home/%s.json' % get_locale().language))

    def get_number(name, mod, chk=True):
        for key in i18n_data.get_data().keys():
            r = regex[name].match(key)
            if r is None:
                continue

            if chk and int(r.group('n')) % 2 != mod:
                continue
            yield r.group('n')

    class AOSDelay:
        def __init__(self):
            self.counter = 100
            self.increment = 100

        def get_delay(self):
            delay = self.counter
            self.counter += self.increment
            return delay

    return dict(
        get_number=get_number,
        get_delay=AOSDelay().get_delay,
        i18n=i18n_data,
        bp_name='home',
    )


@bp_frontend_home.route('/', methods=['GET'])
@access_token_needed
def home_page():
    return render_template('home/index.html')


__all__ = ['bp_frontend_home']
