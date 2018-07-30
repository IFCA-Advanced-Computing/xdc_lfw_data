from celery import Celery
from celery.utils.log import get_task_logger
from wq_modules import clouds
from wq_modules import meteo

import json
from datetime import datetime

app = Celery('tasks',broker='amqp://localhost//')
app.conf.update(
    result_backend='db+mysql://xdc:data$$cloud18@localhost/tasks'
)
@app.task
def cloud_coverage(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = clouds.cloud_coverage(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return {'request_id':result.id}
@app.task
def cloud_mask(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = clouds.cloud_mask(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return {'request_id':result.id}
@app.task
def get_meteo(start_date, end_date, region):
    logger = get_task_logger(__name__)
    logger.info("Adding %s + %s" % (start_date, end_date))
    result = meteo.get_meteo(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'), region)
    return {'request_id':result.id}    
