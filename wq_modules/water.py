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
import matplotlib.pyplot as plt 

from wq_modules import utils
from wq_modules import sentinel
from wq_modules import landsat
#from wq_modules import clouds


def main_water(inidate, enddate, region, action):
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
    
    if action == 'water_mask':
        for file in sentinel_files:
            
            date_path = sentinel_files[file]['path']    
            lon, lat, water_mask = mask("Sentinel-2", date_path)
            
            if 'Water.nc' in os.listdir(date_path):
                continue
        
            #create de netCDF4 file
            utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')
        
        for file in landsat_files:
            
            date_path = landsat_files[file]['path']
            lon, lat, water_mask = mask("Landsat8", date_path)
            
            if 'Water.nc' in os.listdir(date_path):
                continue
        
            #create de netCDF4 file
            utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')
    
    elif action == 'water_surface':
        for file in sentinel_files:
            
            date_path = sentinel_files[file]['path']
            surface("Sentinel-2", date_path)
            
        for file in landsat_files:
            
            date_path = landsat_files[file]['path']
            surface("Landsat8", date_path)
    
    return sentinel_files, landsat_files


def surface(platform, date_path):
    """ Given a satellite image, returns the water surface
        image: file
    """

    lon, lat, water_mask = mask(platform, date_path)

    pixel_area = utils.get_pixel_area(lon, lat)
    water_surface = np.sum(water_mask) * pixel_area
    print ('Area:  {} Hectareas'.format(water_surface/10000))
 
    #create csv data(headers)
    csv_headers = ['file', 'pixel_area (m2)', 'water_surface (Hectares)']
    row = [date_path, pixel_area, water_surface]
    csv_data =[csv_headers]
    csv_data.append(row)
    
    #save csv file
    np.savetxt(os.path.join(date_path, 'water_surface.csv'), csv_data, fmt='%s', delimiter=",")


def mask(platform, date_path):
    
    if platform == 'Sentinel-2':
        
        band_list = ['B03', 'B08']
        lon, lat, bands = utils.load_bands(date_path, band_list)

        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.

        mndwi = (bands['B03'] - bands['B08']) /(bands['B03'] + bands['B08'])
        threshold = filters.threshold_otsu(mndwi.data)
        water_mask = (mndwi > threshold)
#        water_mask = water_mask * (not mask_cloud.all())
        
    elif platform == 'Landsat8':
    
        band_list = ['B3', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)

        mndwi = (bands['B3'] - bands['B5']) /(bands['B3'] + bands['B5'])
        threshold = filters.threshold_otsu(mndwi.data)
        water_mask = (mndwi > threshold)
#        water_mask = water_mask * (not mask_cloud.all())
    
    #plot
    plot_mask(mndwi, water_mask)
    return lon, lat, water_mask


def plot_mask(mndwi, water_mask):
    
    plt.figure(1)
    plt.subplot(121)
    plt.imshow(mndwi)

    plt.subplot(122)
    plt.imshow(water_mask)
    plt.show()