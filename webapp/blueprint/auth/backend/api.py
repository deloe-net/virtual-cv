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
import datetime

from flask import Blueprint
from flask import g
from flask import jsonify
from flask import request

from .forms import get_auth_form
from .security import tokens
from .security import tools
from .security.tools import api_token_needed
from webapp.blueprint.api import bp_api
from webapp.settings import settings_pool as conf

bp_api_auth = Blueprint('auth', __name__, url_prefix='/iam')
bp_api.register_blueprint(bp_api_auth)


@bp_api_auth.route('/verify', methods=['POST'])
def verify():
    form = get_auth_form()
    # Check if a cookie exists
    if g.cookie_found is True:
        return {'errors': {'general': ['err_already_auth']}}
    if not form.validate_on_submit():
        return {'errors': form.errors}

    code = tools.validate_code(request.form.get('code').upper())
    if code is None:
        return {'errors': {'code': ['err_invalid_code']}}
    elif code.expire is not None and code.expire > datetime.datetime.now():
        return {'errors': {'code': ['err_expired_code']}}

    tools.dump_token(tokens.create_access_token(resource='basic'))
    return {'message': 'verification complete'}


@bp_api_auth.route('/create', methods=['POST'])
@api_token_needed
def create():
    code = request.args.get('code').upper().strip().replace(' ', '')
    desc = request.args.get('desc').upper().strip()

    if conf.auth.code_min_length <= len(code) <= conf.auth.code_max_length:
        return jsonify({'errors': {'code': ['err_invalid']}})
    elif tools.validate_code(code) is not None:
        return jsonify({'errors': {'code': ['err_duplicate']}})

    tools.register_code(code, desc)
    return jsonify({'success': True})


__all__ = ['bp_api_auth']
