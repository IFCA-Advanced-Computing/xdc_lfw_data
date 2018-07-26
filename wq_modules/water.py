#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 13:07:32 2018

@author: daniel
"""
#imports here
from skimage import filters
import os
import numpy as np

from wq_modules import utils
from wq_modules import config
from wq_modules import sentinel2
from wq_modules import landsat8


def water_mask(platform, date_path):
    """ Given a satellite image, returns the water mask
        image: netCDF file
    """
    
    if platform == "Sentinel2":
        
        band_list = ['B3', 'B8']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        mndwi = (bands['B3'] - bands['B8']) /(bands['B3'] + bands['B8'])
        threshold = filters.threshold_otsu(mndwi)
        water_mask = (mndwi > threshold)
    
    elif platform == "Landsat8":
        
        band_list = ['B3', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        mndwi = (bands['B3'] - bands['B5']) /(bands['B3'] + bands['B5'])
        threshold = filters.threshold_otsu(mndwi)
        water_mask = (mndwi > threshold)
        print (water_mask)
    
    return lon, lat, water_mask


def create_water_mask(inidate, enddate, region):
    """ Given a satellite image, returns the water mask
        image: netCDF file
    """
    
    sentinel_files = sentinel2.get_sentinel2_raw(inidate,enddate,region)
    landsat_files = landsat8.get_landsat8_raw(inidate,enddate,region)
    
    datasets_path = config.satelite_info['data_path']
    products = []

    #sentinel 2 cloud_mask
    for f in sentinel_files:
        
        #check if the water mask already done
        date_path = os.path.join(datasets_path, region, f)
        if 'Water.nc' in os.listdir(date_path):
            continue
        
        lon, lat, water = water_mask("Sentinel2", date_path)
        
        #create de netCDF4 file
        utils.create_netCDF(date_path, water, lat, lon, 'Water')
        
        #json
        products.append('{}.Water.nc'.format(date_path))
    
    for f in landsat_files:
        
        #check if the water mask already done
        date_path = os.path.join(datasets_path, region, f)
        if 'Water.nc' in os.listdir(date_path):
            continue
        
        lon, lat, water = water_mask("Landsat8", date_path)
        
        #create de netCDF4 file
        utils.create_netCDF(date_path, water, lat, lon, 'Water')
        
        #json
        products.append('{}.Water.nc'.format(date_path))
    
    #json
    data = {'downloaded':{'sentinel 2': sentinel_files, 'landsat 8': landsat_files},
            'action': products}
    
    return data


def water_surface(inidate, enddate, region):
    """ Given a satellite image, returns the water surface
        image: file
    """
    
    sentinel_files = sentinel2.get_sentinel2_raw(inidate, enddate, region)
    landsat_files = landsat8.get_landsat8_raw(inidate ,enddate, region)
    
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
