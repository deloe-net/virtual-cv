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
import datetime
from uuid import uuid4

from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import Model
from peewee import UUIDField

from .database import database_proxy

schema_version = '1.0'
tables = []


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Version(BaseModel):
    version = CharField()
    active = BooleanField(default=True)
    date = DateTimeField(default=datetime.datetime.now)


class OAuth(BaseModel):
    provider = CharField()
    email = CharField(unique=True)
    name = CharField(null=True)
    date = DateTimeField(default=datetime.datetime.now)


class Code(BaseModel):
    uuid = UUIDField(unique=True, default=uuid4)
    code = CharField(unique=True)
    desc = CharField()
    expire = DateTimeField(null=True)
    revoke = BooleanField(default=False)
    date = DateTimeField(default=datetime.datetime.now)


class Last(BaseModel):
    code = ForeignKeyField(Code, backref='acl')
    date = DateTimeField(default=datetime.datetime.now)


tables.extend([Version, Code, OAuth, Last])

__all__ = ['tables', 'Last', 'Code', 'OAuth', 'Version', 'schema_version']
