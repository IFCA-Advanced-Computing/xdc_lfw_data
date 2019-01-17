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
Created on Wed Jul 18 13:07:32 2018

@author: daniel
"""
#imports here
#from skimage import filters
import os
import numpy as np
from skimage import filters 

from wq_modules import utils
from wq_modules import config
from wq_modules import sentinel
from wq_modules import landsat
from wq_modules import clouds


def water_mask(inidate, enddate, region):
    """ Given a satellite image, returns the water mask
        image: netCDF file
    """

    s = sentinel.Sentinel(inidate, enddate, region)
    s.download()
    sentinel_files = s.__dict__['output']

    l = landsat.Landsat(inidate, enddate, region)
    l.download()
    landsat_files = l.__dict__['output']

    for file in sentinel_files:

        date_path = sentinel_files[file]['path']

        if 'Water.nc' in os.listdir(date_path):
            continue

        mask_cloud = clouds.mask('Sentinel-2', date_path)

        band_list = ['B03', 'B08']
        lon, lat, bands = utils.load_bands(date_path, band_list)

        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.

        mndwi = (bands['B03'] - bands['B08']) /(bands['B03'] + bands['B08'])
        
        threshold = filters.threshold_otsu(mndwi.data)
        water_mask = (mndwi > threshold)
        water_mask = water_mask * (not mask_cloud.all())
        
         #create de netCDF4 file
        utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')

    for file in landsat_files:

        date_path = landsat_files[file]['path']
        
        if 'Water.nc' in os.listdir(date_path):
            continue

        mask_cloud = clouds.mask('Landsat8', date_path)

        band_list = ['B3', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)

        mndwi = (bands['B3'] - bands['B5']) /(bands['B3'] + bands['B5'])
        
        threshold = filters.threshold_otsu(mndwi.data)
        water_mask = (mndwi > threshold)
        water_mask = water_mask * (not mask_cloud.all())
        
        #create de netCDF4 file
        utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')


def water_surface(inidate, enddate, region):
    """ Given a satellite image, returns the water surface
        image: file
    """
    
    datasets_path = config.satelite_info['data_path']
    reservoir_path = os.path.join(datasets_path, region)
    
    #create csv data(headers)
    csv_headers = ['file', 'pixel_area', 'water_surface']
    csv_data =[csv_headers]
     
    #sentinel 2 water_mask
    for f in sentinel_files: 
        
        date_path = os.path.join(datasets_path, region, f)
        lon, lat, water = water_mask("Sentinel2", date_path)
        
        pixel_area = utils.get_pixel_area(date_path, ["B1"])
        
        #create csv row
        row = [f, pixel_area, pixel_area*(np.sum(water))]
        csv_data.append(row)
        
    #landsat 8 water_mask
    for f in landsat_files: 
        
        date_path = os.path.join(datasets_path, region, f)
        lon, lat, water = water_mask("Landsat8", date_path)
        
        pixel_area = utils.get_pixel_area(date_path, ["B1"])
        
        #create csv row
        row = [f, pixel_area, pixel_area*(np.sum(water))]
        csv_data.append(row)
        
    #save csv file
    np.savetxt(os.path.join(reservoir_path, 'water_{}.csv'.format(region)), csv_data, fmt='%s', delimiter=",")
    
    #json
    data = {'downloaded':{'sentinel 2': sentinel_files, 'landsat 8': landsat_files},
            'action': os.path.join(reservoir_path, '{}.csv'.format(region))}
    
    return data
