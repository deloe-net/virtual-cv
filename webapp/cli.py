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
import argparse
import sys
from argparse import RawDescriptionHelpFormatter as HelpFormatter

from .assets import AssetsCLI
from .blueprint import auth
from .common import Reactor
from .exceptions import CriticalError
from .settings import EnvironEngine
from .settings import get_vault_engine
from .settings import load_dir
from .settings import set_secret_engine
from .settings import settings_pool as settings


class CustomHelper(HelpFormatter):
    def _format_action(self, action):
        parts = super(HelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = '\n'.join(parts.split('\n')[1:])
        return parts

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return self._metavar_formatter(action, action.dest)(1)

        parts = []
        if action.nargs == 0:
            parts.extend(action.option_strings)
        else:
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            for option_string in action.option_strings:
                parts.append('%s' % option_string)
            parts[-1] += ' %s' % args_string
        return ', '.join(parts)


class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n\n' % message)
        self.print_help()
        sys.exit(2)


class ParserReactor(Reactor):
    def __init__(self, *args, **kwargs):
        self.parser = CustomParser(*args, **kwargs)
        self.sub_parser = self.parser.add_subparsers(
            dest='sub_parser', parser_class=CustomParser
        )
        self.reactors = {}

    def add_reactor(self, reactor):
        self.reactors[reactor.name] = reactor

    def add_parser(self, *args, **kwargs):
        if 'formatter_class' not in kwargs:
            kwargs['formatter_class'] = CustomHelper
        return self.sub_parser.add_parser(*args, **kwargs)

    def process(self, args):
        if args.sub_parser not in self.reactors:
            self.parser.print_help()
            exit(1)

        reactor = self.reactors[args.sub_parser]
        reactor.process(args)


cli_parser = ParserReactor(
    formatter_class=CustomHelper, description='WebApp Command Line: ismael-cv'
)


def main():
    load_dir('config.d/')
    if settings.secret.engine == 'environ':
        engine = EnvironEngine(settings.environ.prefix)
    elif settings.secret.engine == 'vault':
        engine = get_vault_engine()
    else:
        raise CriticalError('Unknown engine')

    set_secret_engine(engine)
    cli_parser.add_reactor(AssetsCLI(cli_parser))
    cli_parser.add_reactor(auth.backend.database.cli.DatabaseCLI(cli_parser))
    cli_parser.add_reactor(auth.backend.security.cli.CodeCLI(cli_parser))
    cli_parser.add_reactor(auth.backend.security.cli.TokenCLI(cli_parser))
    args = cli_parser.parser.parse_args()
    cli_parser.process(args)


if __name__ == '__main__':
    main()
