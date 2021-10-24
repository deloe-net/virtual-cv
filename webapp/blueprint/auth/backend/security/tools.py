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
import uuid
from functools import wraps

from flask import g
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError

from ..database.schema import Code
from .tokens import decode_jwt_token
from .tokens import idp_d
from webapp.logger import logger
from webapp.settings import settings_pool


SECRET_COOKIE_NAME = uuid.uuid4().hex[0:16]

#                       AUTHENTICATE VIA CODE
###############################################################################


def register_code(code: str, desc: str, **kwargs):
    """
    Register an access code. The access code can be alphanumeric with a maximum
    length of 32 characters, it can contain special characters.

    :param code: alphanumeric code
    :param desc: description of who owns the code
    :return: peewee object
    """
    return Code.create(code=code, desc=desc, **kwargs)


def validate_code(code: str):
    """
    if a code is registered returns the database record, otherwise returns None

    :param code: alphanumeric code
    :return: peewee object
    """
    return Code.get_or_none(Code.code == code)


#                       AUTHENTICATE VIA JWT
##############################################################################


def read_jwt_token(jwt_token: str, token_type: str) -> dict:
    """

    :param jwt_token:
    :param token_type:
    :return:
    """
    jwt_data = {}
    try:
        jwt_data = decode_jwt_token(jwt_token)
    except (ExpiredSignatureError, InvalidTokenError,
            InvalidSignatureError) as e:
        logger.error('Invalid Token: %s' % repr(e))
    except Exception as e:
        return logger.exception(e)

    if idp_d.verify_blacklist(payload=jwt_data):
        return logger.error('token blacklisted')

    if token_type is not None and jwt_data['tty'] != token_type:
        return logger.critical('invalid token type????')

    # TODO: Add resource check

    return jwt_data


def set_token_ctx(token_encoded, token_decoded):
    g.token_encoded = token_encoded
    g.token_decoded = token_decoded


def load_token(token_type):
    if '__token' in request.args:
        token_encoded = request.args.get('__token')
        token_decoded = read_jwt_token(token_encoded, token_type)
    elif SECRET_COOKIE_NAME in session:
        token_encoded = session[SECRET_COOKIE_NAME]
        token_decoded = read_jwt_token(token_encoded, token_type)
    else:
        token_encoded = None
        token_decoded = None
    set_token_ctx(token_encoded, token_decoded)
    g.cookie_found = g.token_decoded is not None

    return token_decoded


def dump_token(token):
    session[SECRET_COOKIE_NAME] = token


def token_needed(token_type: str):
    # TODO: add docstrings

    def function_wrap(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if (
                settings_pool.auth.auth_required == 1
                and g.get('token_decoded', None) is None
            ):
                return redirect(url_for('frontend_auth.auth_code'))
            else:
                return f(*args, **kwargs)

        return decorated_function

    return function_wrap


def api_token_needed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if (
            settings_pool.auth.auth_required == 1
            and g.get('token_decoded', None) is None
        ):
            return jsonify({'errors': {'token': ['err_missing_token']}})
        return func(*args, **kwargs)

    return decorated_function


def unauthenticated_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            settings_pool.auth.auth_required == 0
            or g.get('token_decoded', None) is not None
        ):
            return
        return f(*args, **kwargs)

    return decorated_function


access_token_needed = token_needed('access')
