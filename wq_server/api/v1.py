#!/usr/bin/python
from datetime import datetime
from wq_modules import tasks
from pyramid.view import view_config

import json
import MySQLdb

@view_config(renderer='json')
def satellite(request):
#Checks json body not empty
  if request.json_body == '':
    return {'Error':'No JSON body provided'}
  else:
    print(request.json_body)
    data = request.json_body #Data is now a json object
    region = data['region']
    sd = data['start_date'] 
    ed = data['end_date']
    #Check dates
    try:
      start_date = datetime.strptime(sd, "%d-%m-%Y").date()
    except ValueError:
      print("Not a valid date: '{0}'.".format(start_date))
      return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

    try:
      end_date = datetime.strptime(ed, "%d-%m-%Y").date()
    except ValueError:
      print("Not a valid date: '{0}'.".format(end_date))
      return {'Error':'Invalid End date. Format dd-mm-YYYY'}

    action = data['action']
    
    print(region)
    print(action)   
    if region not in ['CdP','Sanabria','Cogotas']:
      return {'Error':'Region not accepted. Accepted regions: CdP, Sanabria, Cogotas'}
        
    #Action management
    if action is not None:
      if action == 'cloud_coverage':
        json_cloud_coverage = tasks.cloud_coverage.delay(start_date, end_date, region)
        return {'request_id' : json_cloud_coverage.id}
      elif action == 'cloud_mask':
        json_cloud_mask = tasks.cloud_mask.delay(start_date, end_date, region)
        return {'request_id' : json_cloud_mask.id}
      elif action == 'water_surface':
        #TODO
        sat_img = sentinel2.get_sentinel2_raw(start_date,end_date,region)
        water_sur = water.water_surface(sat_img)
        return {'water_surface': '1000'}
      elif action == 'water_mask':
        #TODO
        sat_img = sentinel2.get_sentinel2_raw(start_date,end_date,region)
        water_mask = water.water_mask(sat_img)
        return {'water_mask': 'path_to_file'}
      elif action == 'meteo':
        meteo_data = tasks.get_meteo.delay(start_date, end_date, region)
        return {'request_id' : meteo_data.id}
      elif action == 'repos':
        repos_data = tasks.get_dataset.delay(start_date, end_date, region)
        return {'request_id' : repos_data.id}
      else: 
        return {'Error':'No valid action provided. Accepted actions: cloud_mask, cloud_coverage, meteo'}
    else: 
      return {'Error':'No valid action provided. Accepted actions: cloud_mask, cloud_coverage, meteo'}

@view_config(renderer='json')
def status(request):
    if request.json_body == '':
        return {'Error':'No JSON body provided'}
    else:
        print(request.json_body)
        data = request.json_body #Data is now a json object
        request_id = data['request_id']

    #Check job status
    connection=MySQLdb.connect(host='localhost',user='xdc',passwd='data$$cloud18',db='tasks') #TODO from config
    cursor=connection.cursor()

    sql="SELECT status FROM celery_taskmeta where task_id='%s' LIMIT 1" % request_id
    cursor.execute(sql)
    data=cursor.fetchall()
    return {'status': data[0][0]}
