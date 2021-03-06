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
from flask import render_template


def generic_err(page_code):
    return (
        render_template('errors/index.html',
                        page_code=page_code,
                        bp_name='errors'),
        page_code)


def page_not_found(e):
    return generic_err(404)


def forbidden(e):
    return generic_err(403)


__all__ = ['page_not_found', 'forbidden']
