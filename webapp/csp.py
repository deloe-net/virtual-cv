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
import copy
from os.path import splitext
from urllib.parse import urlparse

from flask import g

from .webapp import core


class CSP:
    policy_line = "%s %s;"
    policy_ext = {"css": "style-src", "js": "script-src"}

    def __init__(self):
        self.policies = {}

    def __copy__(self):
        return copy.deepcopy(self)

    def format(self):
        lines = []
        for policy, data in self.policies.items():
            lines.append(self.policy_line % (policy, " ".join(data)))
        return " ".join(lines)

    def add_policy(self, name: str, value: str) -> None:
        if name in self.policies:
            policy = self.policies[name]
        else:
            policy = self.policies[name] = set()
        policy.add(value)

    def add_from_url(self, url: str, name: str = None) -> str:
        sch = urlparse(url)
        if name is None:
            ext = splitext(sch.path)[1].lstrip(".")
            if ext in self.policy_ext:
                name = self.policy_ext[ext]
            else:
                raise ValueError("unknown policy extension")

        value = f"{sch.scheme}://{sch.netloc}"
        self.add_policy(name, value)
        return url

    add = add_from_url

    def bulk_add(self,
                 *policies: str,
                 name: str = None,
                 quote: bool = True) -> None:

        for policy in policies:
            if quote:
                policy = repr(str(policy))
            self.add_policy(name, policy)


csp_policy = CSP()
csp_policy.add_policy("script-src", "https://www.gstatic.com")
csp_policy.add_policy("worker-src", "https://www.google.com")
csp_policy.bulk_add("self", "unsafe-inline", "unsafe-eval", name="script-src")


@core.context_processor
def ctx_csp():
    g.csp = copy.copy(csp_policy)
    return dict(csp=g.csp)
