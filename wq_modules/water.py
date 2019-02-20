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

@author: Daniel Garcia Diaz
"""

#imports here
import os
import numpy as np
from skimage import filters
import matplotlib.pyplot as plt

from wq_modules import config
from wq_modules import utils
from wq_modules import sentinel
from wq_modules import landsat
from wq_modules import metadata_gen
#from wq_modules import clouds


def main_water(sentinel_files, landsat_files, region, action):
    """
        Dowloand Sentinel and landsat files and chose de subfuncion
    """
    
    path = config.datasets_path
        
    for file in sentinel_files:
        
        date_path = os.path.join(path, region, file)
        
        if action == 'water_mask':

            lon, lat, water_mask = mask("Sentinel-2", date_path)

            if 'Water.nc' in os.listdir(date_path):
                continue

            #create de netCDF4 file
            utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')

        elif action == 'water_surface':

            surface("Sentinel-2", date_path)

    for file in landsat_files:
        
        date_path = os.path.join(path, region, file)
        
        if action == 'water_mask':

            lon, lat, water_mask = mask("Landsat8", date_path)

            if 'Water.nc' in os.listdir(date_path):
                continue

            #create de netCDF4 file
            utils.create_netCDF(date_path, water_mask, lat, lon, 'Water')

        elif action == 'water_surface':

            surface("Landsat8", date_path)


def surface(platform, date_path):
    """ Given a satellite image, returns the water surface
        image: file
    """

    lon, lat, water_mask = mask(platform, date_path)

    pixel_area = utils.get_pixel_area(lon, lat)
    water_surface = np.sum(water_mask) * pixel_area
    print ('Area:  {} Hectares'.format(water_surface/10000))

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

    elif platform == 'Landsat8':

        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)

        #MNDWI
        mndwi = (bands['B3'] - bands['B5']) /(bands['B3'] + bands['B5'])
        #Clouds
        mask_cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))
        mask_cloud = mask_cloud.astype(np.float32)

        threshold = filters.threshold_otsu(mndwi.data)
        water_mask = (mndwi > threshold)
        water_mask = water_mask.astype(np.float32)

        water_mask = water_mask - mask_cloud
        water_mask = water_mask.clip(min=0)

    #plot
    plot_mask(mndwi, water_mask)
    return lon, lat, water_mask


def plot_mask(mndwi, water_mask):

    plt.figure(1)
    plt.subplot(121)
    plt.imshow(mndwi, origin='lower')

    plt.subplot(122)
    plt.imshow(water_mask, origin='lower')
    plt.show()
