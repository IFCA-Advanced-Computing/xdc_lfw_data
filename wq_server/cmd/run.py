#!/usr/bin/env python
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

from wq_server import api
from wq_modules import config
from wsgiref.simple_server import make_server
from celery import current_app
from celery.bin import worker
from threading import Thread

def start_celery(app):
    #app = current_app._get_current_object()
    res_bkn = 'db+mysql://' + config.celery_db_user + ':' + config.celery_db_pass + '@localhost/tasks'
    print(res_bkn)
    wk = worker.worker(app=app)
    options = {
        'result_backend': res_bkn,
        'broker': 'amqp://guest:guest@localhost:5672//',
        'loglevel': 'INFO'
    }
    wk.run()

def start_web():
    web_app = api.get_app()
    server = make_server('0.0.0.0', 6543, web_app)
    server.serve_forever()

def main():
    t1 = Thread(target=start_celery, args=[current_app._get_current_object()])
    t2 = Thread(target=start_web, args=[])
   
    t1.start()
    t2.start()

if __name__ == "__main__":
    main()
