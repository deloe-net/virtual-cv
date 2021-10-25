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
import uuid
from typing import Union

import jwt

ACCESS_TOKEN = 'access'
DEFAULT_ALGM = 'HS256'


class JWT:
    RESOURCE_SEP = ';'

    def __init__(self, algm: str, secret_key: str = None):
        self.__algm = algm
        self.__secret_key = secret_key

    @property
    def resource_sep(self):
        return self.RESOURCE_SEP

    def update_secret_key(self, secret_key: str):
        self.__secret_key = secret_key

    def update_algm(self, algm: str):
        self.__algm = algm

    @property
    def secret(self):
        return self.__secret_key

    @property
    def algm(self):
        return self.__algm


class TokenIssuer(JWT):
    DEFAULT_TTL = 3600 * 24 * 7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token_ttl = {ACCESS_TOKEN: self.DEFAULT_TTL}

    @property
    def token_ttl(self) -> dict:
        return self._token_ttl

    def get_token_ttl(self, token_type: str):
        return self.token_ttl.get(token_type)

    def update_ttl(self, token_type, ttl):
        self.token_ttl[token_type] = ttl

    def format_resources(self, resource: Union[list, tuple, str]) -> str:
        if isinstance(resource, str):
            resource = (resource,)

        return self.resource_sep.join([res.strip() for res in resource if res])

    def create_payload(self, **kwargs):
        date = datetime.datetime.utcnow()
        ttl = self.get_token_ttl(token_type=kwargs['tty'])
        if kwargs.get('resource'):
            kwargs['res'] = self.format_resources(kwargs.pop('resource'))

        pld = {
            'exp': date + datetime.timedelta(ttl),
            'iat': date,
            'nbf': date,
            'jti': str(uuid.uuid4()),
        }
        pld.update(kwargs)
        return pld

    def _encode_token(self, token_type: str, **kwargs) -> str:
        payload = self.create_payload(tty=token_type, **kwargs)
        return jwt.encode(payload, self.secret, algorithm=self.algm)

    def encode_token(self, token_type: str, **kwargs) -> str:
        if token_type not in self.token_ttl:
            raise ValueError('token type not supported: "%s"' % token_type)
        return self._encode_token(token_type, **kwargs)


class TokenReceiver(JWT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__blacklist = set()

    def decode_token(self, jwt_token):
        return jwt.decode(jwt_token, self.secret, algorithms=self.algm)

    def blacklist_token(self, jti: str) -> None:
        self.__blacklist.add(jti)

    def verify_blacklist(self, payload: dict) -> bool:
        return payload.get('jti') in self.__blacklist


idp_e = TokenIssuer(DEFAULT_ALGM)
idp_d = TokenReceiver(DEFAULT_ALGM)


def create_access_token(resource, **kwargs):
    return idp_e.encode_token(ACCESS_TOKEN, resource=resource, **kwargs)


def decode_jwt_token(jwt_token):
    return idp_d.decode_token(jwt_token)
