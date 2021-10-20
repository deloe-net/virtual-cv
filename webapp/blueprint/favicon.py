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
import os

from flask import send_from_directory as send

from ..webapp import core


_static = os.path.join(core.static_folder, 'multimedia/images')


@core.route('/favicon.ico')
def favicon():
    return send(_static, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
