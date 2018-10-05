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

from celery import Celery
from celery.utils.log import get_task_logger
from wq_modules import repos
from wq_modules import clouds
from wq_modules import meteo

import json
from datetime import datetime

app = Celery('tasks',broker='amqp://localhost//')

@app.task
def cloud_coverage(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = clouds.cloud_coverage(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return result
@app.task
def cloud_mask(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = clouds.cloud_mask(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return result
@app.task
def get_meteo(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = meteo.get_meteo(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return result
@app.task
def get_dataset(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = repos.get_dataset(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return result 
