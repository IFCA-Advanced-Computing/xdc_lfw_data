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

"""
Given two dates and region, download N raw images of Landsat-8 from earth engine
inidate: datetime
enddate: datetime
region: name of one of the reservoirs saved in the "coord_reservoirs.json" file

Author: Daniel Garcia
Date: May 2018
"""
#imports api
import os
import json
import datetime
import shutil
import requests

#imports subfunctions
from wq_modules import utils
from wq_modules import config 

#earth engine
import ee
ee.Initialize()

def get_landsat8_raw(inidate,enddate,region):
    """ 
    Given two dates and region, download N raw images

    Parameters
    ----------
    inidate: datetime
          initial date
    enddate: datetime
          End date
    region: Array with 4 coordinates
 
    Returns
    -------
    List of files
    """
    if (config.onedata_mode == 1):
        datasets_path = '/onedata/' + config.onedata_user + '/' + config.onedata_space + '/' + config.download_datasets
    else:
        datasets_path = '.' + config.satelite_info['data_path']
    
    reservoir_path = os.path.join(datasets_path, region)
    files = []

    metadata = {'scale': 30, # grid resolution
                'start_date': inidate.strftime("%d/%m/%y"), # dd-mm-yyyy
                'end_date': enddate.strftime("%d/%m/%y"), # dd-mm-yyyy
                'delta_days': 7 # time periodicity
                }
     
    # Add reservoir coordinates to search_metadata
    metadata['coord'] = config.regions['regions'][region]
     
    # Download
    query_dict = {'scale': metadata['scale'],
                  'region': str(metadata['coord'])
                  }
    
    delta = datetime.timedelta(metadata['delta_days'])
    d1, d2 = inidate - delta, inidate  # time intervals [d1, d2]
    
    #search files in earth engine
    while d1 < enddate:
    
        d1, d2 = d2, d2 + delta
        try:
            sat_dict = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')
            sat_dict = sat_dict.filterBounds(ee.Geometry.Polygon([metadata['coord']]))
            sat_dict = sat_dict.filterDate(str(d1), str(d2))
            sat_list = sat_dict.toList(1)
            id_fecha = sat_list.getInfo()[0]['properties']['DATE_ACQUIRED']
            image = sat_dict.mosaic()
            print ('Images found for range {} - {}'.format(d1, d2))
            
            #list of the files and metadata files
            files.append(id_fecha)
            file_metadata = utils.metadata_file('Landsat8', sat_list)
                
        except:
            print ('No images found for range {} - {}'.format(d1, d2))
            continue
       
        #except by file already downloaded
        utils.check_file(datasets_path)
        with open(os.path.join(datasets_path, 'downloaded_files.json')) as data_file:    
            downloaded_files = json.load(data_file)
        
        if id_fecha in downloaded_files['Landsat 8'][region]:
            print ("    file {} already downloaded".format(id_fecha))
            continue
        
        print ('    Downloading {} files'.format(id_fecha))
        date_path = os.path.join(reservoir_path, '{}'.format(id_fecha))
        shutil.rmtree(date_path, ignore_errors=True)
        
        band_url = image.getDownloadURL(query_dict)
        utils.download_zip(band_url, date_path)
        utils.tiff_to_netCDF(date_path)
        
        # Save the new list of files
        downloaded_files['Landsat 8'][region].append(id_fecha)
        with open(os.path.join(datasets_path, 'downloaded_files.json'), 'w') as outfile:
            json.dump(downloaded_files, outfile)
        
        # Save landsat-8 file metadata
        with open(os.path.join(date_path, '{}.json'.format(id_fecha)), 'w') as outfile:
            json.dump(file_metadata, outfile)
    
        # Onedata metadata attachment
        if (config.onedata_mode == 1):
            #TODO change token
            header_json = {'X-Auth-Token': 'MDAxNWxvY2F00aW9uIG9uZXpvbmUKMDAzMGlkZW500aWZpZXIgMDRmMGQxODRmMTBmODAxN2ZkNTNkNGJlYWIyNjc3NTkKMDAxYWNpZCB00aW1lIDwgMTU2MzM00NDg00MQowMDJmc2lnbmF00dXJlIGy97Y8H4rGIxCMYsJSHQg1v6BpLGAwnDL01EE6AFAs1BCg', 'Content-type' : 'application/json'}
            try:
                print(file_metadata)
                print(config.onedata_url+config.onedata_api+'metadata/'+ config.onedata_space + '/' + config.download_datasets + '/' + region + '/' + '{}'.format(id_fecha))
                r = requests.put(config.onedata_url+config.onedata_api+'metadata/'+ config.onedata_space + '/' + config.download_datasets + '/' + region + '/' + '{}'.format(id_fecha),headers=header_json,data=json.dumps(file_metadata))
                print(r.text)
            except requests.exceptions.RequestException as e:
                print(e)
                continue
    
    return files
