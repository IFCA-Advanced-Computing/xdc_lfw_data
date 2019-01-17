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

import os
import json
import numpy as np
from datetime import datetime

from wq_modules import utils
from wq_modules import config
from wq_modules import sentinel
from wq_modules import landsat

def cloud_coverage(inidate, enddate, region):
    """ Given a satellite image, returns the cloud covarage
        image: file
        input
    """
    
    datasets_path = config.satelite_info['data_path']
    reservoir_path = os.path.join(datasets_path, region)
    
    #create csv data(headers)
    csv_headers = ['file', 'cloud_coverage']
    csv_data =[csv_headers]
    
    #find cloud coverage in metadata
    for f in sentinel_files+landsat_files:
        dir_path = os.path.join(reservoir_path, f)

        with open(os.path.join(dir_path, '{}.json'.format(f))) as data_file:    
            metadata_file = json.load(data_file)
        cloud_coverage = metadata_file['cloud_coverage']
        
        #create csv row
        row = [f, cloud_coverage]
        csv_data.append(row)

    #save csv file
    np.savetxt(os.path.join(reservoir_path, '{}.csv'.format(region)), csv_data, fmt='%s', delimiter=",")
    
    #json
    data = {'downloaded':{'sentinel 2': sentinel_files, 'landsat 8': landsat_files},
            'action': os.path.join(reservoir_path, '{}.csv'.format(region))}
    return data


def cloud_mask(inidate, enddate, region):
    """ Given a satellite image, returns the cloud mask
        image: netCDF file
    """
    
    s = sentinel.Sentinel(inidate, enddate, region)
    s.download()
    sentinel_files = s.__dict__['output']
    
    l = landsat.Landsat(inidate, enddate, region)
    l.download()
    landsat_files = l.__dict__['output']
    
    #sentinel 2 cloud_mask
    for file in sentinel_files:
        
        date_path = sentinel_files[file]['path']
        
        #check if the cloud mask already done
        if 'Cloud.nc' in os.listdir(date_path):
            continue
    
        band_list = ['B04']
        lon, lat, bands = utils.load_bands(date_path, band_list)
    
        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.
    
#        ndsi = (bands['B03'] - bands['B11']) / (bands['B03'] + bands['B11']) #vegetation index
    
        #filters to discriminate clouds
        mask_cloud = (bands['B04'] > 0.07) * (bands['B04'] < 0.25) # are passed to Step 1.b 
#        mask_cloud = bands['B04'] > 0.25 # Clouds , are passed to step2
#        mask_cloud = mask_cloud + mask_potential_cloud * (ndsi > -0.16)) # are passed to Step 2
        
        #create de netCDF4 file
        utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')

    #landsat 8 cloud mask
    for file in landsat_files:
        
        #check if the cloud mask already done
        date_path = landsat_files[file]['path']
        
        if 'Cloud.nc' in os.listdir(date_path):
            continue
        
        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        #Clouds
        mask_cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))

        #create de netCDF4 file
        utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')
        
def mask(platform, date_path):

    if platform == 'Sentinel-2':
        
        band_list = ['B04']
        lon, lat, bands = utils.load_bands(date_path, band_list)
    
        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.
    
        mask_cloud = (bands['B04'] > 0.07) * (bands['B04'] < 0.25)
    
    elif platform == 'Landsat8':
        
        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        #Clouds
        mask_cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))
    
    return mask_cloud
        
        