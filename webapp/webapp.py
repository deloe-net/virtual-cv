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
from flask import Flask
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect


core = Flask(__name__, static_folder="assets/dist")

babel = Babel()
babel.init_app(core)

csrf = CSRFProtect()
csrf.init_app(core)
core.config.update(SERVER_NAME="ismael-cv.deloe.net")
