#  Copyright 2021 Ismael Lugo <ismaelrlg.dev@gmail.com>
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
from flask import Blueprint
from flask import render_template
from flask_babel import get_locale
from flask_wtf import csrf

from ..backend import oauth
from ..backend.forms import get_auth_form
from ..backend.security.tools import unauthenticated_only
from webapp.assets import sf
from webapp.locales import i18n
from webapp.webapp import core

bp_frontend_auth = Blueprint('frontend_auth', __name__, url_prefix='/auth')


@bp_frontend_auth.context_processor
def ctx_auth():
    i18n_data = i18n.load(sf('locales/auth/%s.json' % get_locale().language))

    return dict(
        i18n=i18n_data,
        public_key=core.config['RECAPTCHA_PUBLIC_KEY'],
        bp_name='auth',
        oauth=oauth.callbacks,
    )


@bp_frontend_auth.route('/', methods=['GET'])
@unauthenticated_only
def auth_code():
    csrf.generate_csrf()
    return render_template('auth/index.html', form=get_auth_form())


__all__ = ['bp_frontend_auth']
