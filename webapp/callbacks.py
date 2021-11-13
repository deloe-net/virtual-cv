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
from .settings import get_secret
from .webapp import core


@core.after_request
def add_headers(response):
    """
    - Content-Security-Policy HTTP response header helps to reduce XSS risks on
      modern browsers by declaring, which dynamic resources are allowed to load

    - Security layer to prevent the site from being loaded in a a <frame>,
      <iframe>, <embed> or <object>. This is used to avoid click-jacking
      attacks, ensuring that the content is not embedded into other sites.

      The current policy is SAMEORIGIN, that is, it is only allowed to embed in
      the same site
    """

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    return response


class MainCTX:
    data = None

    @classmethod
    def init(cls):
        cls.data = dict(len=len, G_ANALYTICS_ID=get_secret('G_ANALYTICS_ID'))


@core.context_processor
def built_in():
    return MainCTX.data
