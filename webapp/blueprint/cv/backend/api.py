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
import io
import os

from flask import Blueprint
from flask import g
from flask import send_file as send
from flask import url_for

from .qr import qr
from webapp.blueprint.api import bp_api
from webapp.blueprint.auth.backend.security import tools
from webapp.locales import get_locale
from webapp.settings import settings_pool as settings

bp_api_cv = Blueprint('api_cv', __name__, url_prefix='/cv')
bp_api.register_blueprint(bp_api_cv)


@bp_api_cv.route('/qr.png', methods=['GET'])
def qr_img():
    g.no_json = True
    buf = io.BytesIO()
    url = url_for('api_v1.api_cv.download',
                  __token=[g.token_encoded],
                  _external=True)
    img = qr.get_qr_code(url)
    img.save(buf, format='PNG')
    buf.seek(0)
    return send(buf, mimetype='image/png')


@bp_api_cv.route('/download', methods=['GET'])
def download():
    lang = get_locale().language
    level = 'full' if tools.is_authenticated() else 'limited'

    path = settings.cv.source_path.format(user_lang=lang, level=level)
    if not os.path.exists(path):
        return 'error'
    return send(path, mimetype=settings.cv.mimetype)


__all__ = ['bp_api_cv']
