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
from flask import redirect
from flask import request
from flask import session as cookie
from flask import url_for
from flask_wtf import csrf
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from wtforms import ValidationError

from .common import oauth_callback
from .common import oauth_redirect
from webapp.settings import get_secret


PROVIDER = 'linkedin'


class OAuth(object):
    secrets = None

    class ClientSecrets:
        def __init__(self):
            self.client_id = get_secret('LINKEDIN_CID')
            self.client_secret = get_secret('LINKEDIN_CST')
            self.uri_auth = 'https://www.linkedin.com/uas/oauth2/authorization'
            self.uri_token = 'https://www.linkedin.com/uas/oauth2/accessToken'
            self.scope = ['r_liteprofile', 'r_emailaddress']

    @classmethod
    def init_secrets(cls):
        cls.secrets = cls.ClientSecrets()


@oauth_redirect(PROVIDER)
def oauth_linkedin_redirect():
    session = OAuth2Session(
        OAuth.secrets.client_id,
        redirect_uri=url_for(
                'api_v1.auth.oauth_callback_url', name=PROVIDER, _external=True
            ),
        scope=OAuth.secrets.scope,
        state=csrf.generate_csrf,
    )
    session = linkedin_compliance_fix(session)
    url_auth, state = session.authorization_url(OAuth.secrets.uri_auth)
    return redirect(url_auth)


@oauth_callback(PROVIDER)
def oauth_linkedin_callback():
    try:
        csrf.validate_csrf(cookie.get('csrf_token'))
    except ValidationError:
        abort(400, 'Invalid CSRF token.')

    session = OAuth2Session(OAuth.secrets.client_id,
                            state=cookie.get('csrf_token'))
    session.fetch_token(
        OAuth.secrets.uri_token,
        client_secret=OAuth.secrets.client_secret,
        authorization_response=request.url,
    )
