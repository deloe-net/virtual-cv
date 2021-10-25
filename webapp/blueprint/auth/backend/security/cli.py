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
from humanfriendly import parse_timespan
from playhouse import db_url

from . import tokens
from . import tools
from ..database.database import database_proxy
from webapp.common import Reactor
from webapp.settings import get_secret
from webapp.settings import settings_pool as settings


class CodeCLI(Reactor):
    def __init__(self, parent):
        self.name = 'code'
        self.parser = parent.add_parser(self.name,
                                        help='Actions with access codes')
        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-i',
            '--info',
            help='propagates changes to models in the database schema.',
            metavar='<code>',
            type=str,
        )
        group.add_argument(
            '-c',
            '--create',
            help='Create a new access code',
            nargs=2,
            metavar=('<code>', '<desc>'),
            type=str,
        )
        group.add_argument(
            '-r',
            '--revoke',
            help='Shows the current version of the database schema',
            metavar='<code>',
            type=str,
        )

    @staticmethod
    def init_db():
        database_url = get_secret('AUTH_DATABASE_URL')
        database_proxy.initialize(db_url.connect(database_url))

    @staticmethod
    def info(code):
        code = tools.validate_code(code)
        if code is None:
            print('Error: code not found.')
            return

        print('UUID: %s' % code.uuid)
        print('CODE: %s' % code.code)
        print('DESC: %s' % code.desc)
        print('EXPIRE DATE: %s' % code.expire)
        print('REVOKED: %s' % code.revoke)
        print('ISSUE DATE: %s' % code.date)

    def process(self, args):
        self.init_db()
        if args.create:
            tools.register_code(args.create[0], args.create[1])
        elif args.info:
            self.info(args.info)
        else:
            self.parser.print_help()


class TokenCLI(Reactor):
    def __init__(self, parent):
        self.name = 'token'
        self.parser = parent.add_parser(self.name, help='Actions with tokens')
        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-d',
            '--decode',
            help='Check if a token is valid, decode it and show its content.',
            metavar='<token>',
            type=str,
        )
        group.add_argument(
            '-c',
            '--create',
            help='Generate a new access token.',
            metavar='<resource>',
            type=str,
        )
        group.add_argument(
            '-r',
            '--revoke',
            help='Add a token to the blacklist.',
            metavar='<token>',
            type=str,
        )

    @staticmethod
    def create_token(resource, **kwargs):
        print(tokens.create_access_token(resource=resource, **kwargs))

    @staticmethod
    def decode_token(token):
        print(tokens.decode_jwt_token(token))

    def process(self, args):
        tokens.idp_e.update_secret_key(get_secret('JWT_ENCODE_KEY'))
        tokens.idp_e.update_algm(settings.auth.cipher_algorithm)
        tokens.idp_e.update_ttl(
            'access', parse_timespan(settings.auth.access_token_ttl)
        )
        tokens.idp_d.update_secret_key(get_secret('JWT_DECODE_KEY'))
        tokens.idp_d.update_algm(settings.auth.cipher_algorithm)
        if args.create:
            self.create_token(args.create)
        elif args.decode:
            self.decode_token(args.decode)
