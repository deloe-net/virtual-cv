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
from flask_wtf import FlaskForm
from flask_wtf import RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length

from webapp.settings import settings_pool as config


def get_auth_form(init=True):
    class AuthForm(FlaskForm):
        code = StringField(
            'code',
            validators=[
                DataRequired(message='err_missing_code'),
                Length(
                    min=config.auth.code_min_length,
                    max=config.auth.code_max_length,
                    message='err_code_out_length',
                ),
            ],
        )
        recaptcha = RecaptchaField()

    return AuthForm() if init else AuthForm
