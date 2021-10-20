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
from . import errors
from . import favicon
from .api import bp_api
from .auth import bp_frontend_auth
from .cv import bp_api_cv
from .home import bp_frontend_home
from .privacy import bp_frontend_pp
from .tac import bp_frontend_tac
from webapp.webapp import core

core.register_blueprint(bp_api)

__all__ = [
    'favicon',
    'errors',
    'bp_api',
    'bp_frontend_auth',
    'bp_api_cv',
    'bp_frontend_home',
    'bp_frontend_pp',
    'bp_frontend_tac',
]
