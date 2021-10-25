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
from flask import redirect
from flask import render_template
from flask import url_for

from .index import bp_frontend_auth
from webapp.settings import settings_pool


@bp_frontend_auth.route('/oauth', methods=['GET'])
def oauth_page():
    if settings_pool.auth.code_supply_method == 'oauth-auto':
        return redirect(url_for('frontend_home.home_page'))
    return render_template('auth/oauth.html')
