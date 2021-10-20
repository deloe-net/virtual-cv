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
from flask import Blueprint
from flask import render_template

from webapp.settings import settings_pool as settings

bp_frontend_pp = Blueprint('frontend_pp', __name__, url_prefix='/privacy')


@bp_frontend_pp.context_processor
def ctx_tac():
    return dict(bp_name='privacy', review_date=settings.privacy.review_date)


@bp_frontend_pp.route('/', methods=['GET'])
def privacy_page():
    return render_template('privacy/index.html')


__all__ = ['bp_frontend_pp']
