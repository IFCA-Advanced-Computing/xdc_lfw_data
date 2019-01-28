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
import numpy as np
import matplotlib.pyplot as plt 

from wq_modules import utils
from wq_modules import sentinel
from wq_modules import landsat


def main_cloud(inidate, enddate, region, action):
    """
        Dowloand Sentinel and landsat files and chose de subfuncion
    """
    
    #download sentinel files
    s = sentinel.Sentinel(inidate, enddate, region)
    s.download()
    sentinel_files = s.__dict__['output']

    #download landsat files
    l = landsat.Landsat(inidate, enddate, region)
    l.download()
    landsat_files = l.__dict__['output']

    if action == 'cloud_mask':
        for file in sentinel_files:
            
            date_path = sentinel_files[file]['path']
            lon, lat, mask_cloud = mask('Sentinel-2', date_path)
            
            if 'Cloud.nc' in os.listdir(date_path):
                continue
        
            #create de netCDF4 file
            utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')
        
        for file in landsat_files:
            
            date_path = landsat_files[file]['path']
            lon, lat, mask_cloud = mask('Landsat8', date_path)
            
            if 'Cloud.nc' in os.listdir(date_path):
                continue
        
            #create de netCDF4 file
            utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')
            
    elif action == 'cloud_coverage':
        for file in sentinel_files:
            
            date_path = sentinel_files[file]['path']
            cloud_coverage('Sentinel-2', date_path)
            
        for file in landsat_files:
            
            date_path = landsat_files[file]['path']
            cloud_coverage('Landsat8', date_path)
    
    return sentinel_files, landsat_files
            

def mask(platform, date_path):
    
    if platform == 'Sentinel-2':
        
        band_list = ['B04']
        lon, lat, bands = utils.load_bands(date_path, band_list)
    
        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.
        
#        B11_resize = np.resize(bands['B11'], bands['B03'].shape)
#        ndsi = (bands['B03'] - B11_resize) / (bands['B03'] + B11_resize) #vegetation index
    
        #filters to discriminate clouds
        mask_cloud = (bands['B04'] > 0.07) * (bands['B04'] < 0.25) # are passed to Step 1.b 
#        mask_cloud = bands['B04'] > 0.25 # Clouds , are passed to step2
#        mask_cloud = mask_cloud + (mask_potential_cloud * (ndsi.data > -0.16)) # are passed to Step 2
        
    elif platform == 'Landsat8':
        
        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        #Clouds
        mask_cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))

    plt.figure(1)
    plt.imshow(mask_cloud, origin='lower')
    plt.show()
    return lon, lat, mask_cloud
        

def cloud_coverage(platform, date_path):
    """ Given a satellite image, returns the cloud covarage
        image: file
        input
    """
    
    lon, lat, mask_cloud = mask(platform, date_path)
    coverage = round((np.sum(mask_cloud) * 100) / (mask_cloud.shape[0] * mask_cloud.shape[1]), 2)
    
    plt.figure(1)
    plt.imshow(mask_cloud, origin='lower')
    plt.show()
    
    print ('Cloud coverage:   {} %'.format(coverage))
    
    #create csv data(headers)
    csv_headers = ['file', 'cloud_coverage (%)']
    row = [date_path, coverage]
    csv_data =[csv_headers]
    csv_data.append(row)
    
    #save csv file
    np.savetxt(os.path.join(date_path, 'water_surface.csv'), csv_data, fmt='%s', delimiter=",")