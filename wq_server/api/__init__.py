# -*- coding: utf-8 -*-

# Copyright 2018 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from wq_server.api import v1

config = Configurator()

config.add_route('satellite', '/satellite')
config.add_route('status', '/status')

config.add_view(v1.satellite, route_name='satellite', renderer='json')
config.add_view(v1.status, route_name='status', renderer='json')

app = config.make_wsgi_app()
#server = make_server('0.0.0.0', 6543, app)
#server.serve_forever()

def get_app():
    # This code needs to be refactores, we are currntly accessing the models
    # from two different places, both from loading and from models, and we need
    # to add a single interface.
    print("Loaded models ")
    return app
