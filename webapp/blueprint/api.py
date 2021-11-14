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

from flask import Blueprint
from flask import g
from flask_wtf.csrf import CSRFError

bp_api = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@bp_api.after_request
def auto_api_json(response):
    if not g.get('no_json', False):
        try:
            data = json.loads(response.get_data())
        except json.decoder.JSONDecodeError:
            pass
        else:
            data['success'] = 'errors' not in data
            response.data = json.dumps(data)

    return response


@bp_api.errorhandler(CSRFError)
def handle_csrf_error(e) -> dict:
    return dict(errors={'csrf': e.description})


__all__ = ['bp_api']
