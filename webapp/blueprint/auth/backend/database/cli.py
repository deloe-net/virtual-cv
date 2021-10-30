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
from playhouse import db_url

from .database import database_proxy
from .schema import tables
from webapp.common import Reactor
from webapp.settings import get_secret


class DatabaseCLI(Reactor):
    def __init__(self, parent):
        self.name = 'database'
        self.parser = parent.add_parser(self.name, help='Actions in database')
        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-m',
            '--migrate',
            help='propagates changes to models in the database schema.',
            action='store_true',
        )
        group.add_argument(
            '-i',
            '--init',
            help='Create the initial scheme in the database.',
            action='store_true',
        )
        group.add_argument(
            '-v',
            '--version',
            help='Shows the current version of the database schema',
            action='store_true',
        )

    @staticmethod
    def init_db():
        database_url = get_secret('AUTH_DATABASE_URL')
        database_proxy.initialize(db_url.connect(database_url))

    @staticmethod
    def create(db_tables):
        database_proxy.connect()
        database_proxy.create_tables(db_tables, safe=True)
        database_proxy.close()
        print('OK.')

    def migrate(self):
        pass

    def process(self, args):
        self.init_db()
        if args.init:
            self.create(tables)
        elif args.migrate:
            self.migrate()
        else:
            self.parser.print_help()
