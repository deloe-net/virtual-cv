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

from humanfriendly import parse_timespan
from playhouse import db_url

from webapp.assets import assets
from webapp.assets import sf
from webapp.blueprint import auth
from webapp.blueprint import cv
from webapp.callbacks import MainCTX
from webapp.exceptions import CriticalError
from webapp.locales import load_available_languages
from webapp.settings import EnvironEngine
from webapp.settings import get_secret
from webapp.settings import get_vault_engine
from webapp.settings import load_dir
from webapp.settings import set_secret_engine
from webapp.settings import settings_pool as settings
from webapp.webapp import core


def main(start: bool = False):
    load_dir('config.d/')
    if settings.secret.engine == 'environ':
        engine = EnvironEngine(settings.environ.prefix)
    elif settings.secret.engine == 'vault':
        engine = get_vault_engine()
    else:
        raise CriticalError('Unknown engine')

    set_secret_engine(engine)
    load_available_languages(settings.locales.available_languages)

    if settings.auth.security_level >= 1:
        auth.backend.database.database_proxy.initialize(
            db_url.connect(get_secret('AUTH_DATABASE_URL')))

        auth.backend.security.idp_e.update_secret_key(
            get_secret('JWT_ENCODE_KEY'))
        auth.backend.security.idp_e.update_algm(settings.auth.cipher_algorithm)
        auth.backend.security.idp_e.update_ttl(
            'access', parse_timespan(settings.auth.access_token_ttl))
        auth.backend.security.idp_d.update_secret_key(
            get_secret('JWT_DECODE_KEY'))
        auth.backend.security.idp_d.update_algm(settings.auth.cipher_algorithm)

        auth.backend.oauth.github.OAuth.init_secrets()
        auth.backend.oauth.linkedin.OAuth.init_secrets()

    MainCTX.init()
    assets.update_salt(get_secret('ASSETS_SALT', default=os.urandom(2048)))
    cv.backend.qr.add_logo(os.path.join(core.static_folder,
                                        sf('multimedia/images/avtar.png')))
    core.config.update(
        SERVER_NAME=settings.server.domain_name,
        WTF_CSRF_SECRET_KEY=os.urandom(2048),
        SECRET_KEY=os.urandom(2048),
        RECAPTCHA_PUBLIC_KEY=get_secret('RECAPTCHA_PUBLIC_KEY'),
        RECAPTCHA_PRIVATE_KEY=get_secret('RECAPTCHA_PRIVATE_KEY'),
        SESSION_COOKIE_DOMAIN=settings.server.domain_name,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_PATH='/'
    )
    if start:
        core.run(debug=settings.server.debug_mode)
    else:
        return core


if __name__ == '__main__':
    main(start=True)
