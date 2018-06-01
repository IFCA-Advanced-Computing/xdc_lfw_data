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

import flask
import flask_restplus

import xdc_lfw_data
from xdc_lfw_data.api import v1
from xdc_lfw_data import modules

app = flask.Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

api = flask_restplus.Api(
    app,
    version=deepaas.__version__,
    title='XDC LifeWatch endpoint',
    description='XDC-LifeWatch service for data integration',
)

api.add_namespace(v1.api, path="/api")


def get_app():
    # This code needs to be refactores, we are currntly accessing the models
    # from two different places, both from loading and from models, and we need
    # to add a single interface.
    print("Loaded models %s" % loading.get_available_model_names())
    return app
