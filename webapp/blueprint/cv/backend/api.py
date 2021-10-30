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

from flask import Blueprint
from flask import g
from flask import send_file as send
from flask import url_for

from .qr import qr
from webapp.blueprint.api import bp_api

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
    return 'download'


__all__ = ['bp_api_cv']
