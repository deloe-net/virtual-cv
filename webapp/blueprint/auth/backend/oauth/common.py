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
from flask import abort

from ..api import bp_api_auth

callbacks = {}


@bp_api_auth.route('/oauth/<string:name>/callback', methods=['POST'])
def oauth_callback_url(name):
    if name not in callbacks:
        abort(404)
    return callbacks[name]['callback']()


@bp_api_auth.route('/oauth/<string:name>')
def oauth_redirect_url(name):
    if name not in callbacks:
        abort(404)
    return callbacks[name]['redirect']()


def add_callback(name, callback, cat):
    if name in callbacks:
        data = callbacks[name]
    else:
        data = callbacks[name] = {}
    data[cat] = callback


def oauth_callback(name):
    def dummy_wrap(func):
        add_callback(name, func, 'callback')
        return func

    return dummy_wrap


def oauth_redirect(name):
    def dummy_wrap(func):
        add_callback(name, func, 'redirect')
        return func

    return dummy_wrap


__all__ = ['add_callback', 'oauth_callback', 'oauth_redirect', 'callbacks']
