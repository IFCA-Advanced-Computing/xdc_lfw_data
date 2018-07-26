#TODO
#imports here

import os
import json
import numpy as np
from datetime import datetime

from wq_modules import utils
from wq_modules import config
from wq_modules import sentinel2
from wq_modules import landsat8

def cloud_coverage(inidate, enddate, region):
    """ Given a satellite image, returns the cloud covarage
        image: file
        input
    """
    sentinel_files = sentinel2.get_sentinel2_raw(inidate.date(),enddate.date(),region)
    landsat_files = landsat8.get_landsat8_raw(inidate.date(),enddate.date(),region)
    
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
    
    sentinel_files = sentinel2.get_sentinel2_raw(inidate,enddate,region)
    landsat_files = landsat8.get_landsat8_raw(inidate,enddate,region)
    
    datasets_path = config.satelite_info['data_path']
    products = []
    
    #sentinel 2 cloud_mask
    for f in sentinel_files:
        #check if the cloud mask already done
        date_path = os.path.join(datasets_path, region, f)
        if 'Cloud.nc' in os.listdir(date_path):
            continue
    
        band_list = ['B3', 'B4', 'B11']
        lon, lat, bands = utils.load_bands(date_path, band_list)
    
        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.
    
        ndsi = (bands['B3'] - bands['B11']) / (bands['B3'] + bands['B11']) #vegetation index
    
        #filters to discriminate clouds
        mask_potential_cloud = (bands['B4'] > 0.07) * (bands['B4'] < 0.25) # are passed to Step 1.b 
        mask_cloud = bands['B4'] > 0.25 # Clouds , are passed to step2
        mask_cloud = mask_cloud + (mask_potential_cloud * (ndsi > -0.16)) # are passed to Step 2
        
        #create de netCDF4 file
        utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')
        
        #json
        products.append('{}.Cloud.nc'.format(date_path))
    
    #landsat 8 cloud mask
    for f in landsat_files:
        #check if the cloud mask already done
        date_path = os.path.join(datasets_path, region, f)
        if 'Cloud.nc' in os.listdir(date_path):
            continue
        
        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        lon, lat, bands = utils.load_bands(date_path, band_list)
        
        #Clouds
        mask_cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))

        #create de netCDF4 file
        utils.create_netCDF(date_path, mask_cloud, lat, lon, 'Cloud')
        
        #json
        products.append('{}.Cloud.nc'.format(date_path))
        
    #json
    data = {'downloaded':{'sentinel 2': sentinel_files, 'landsat 8': landsat_files},
            'action': products}
    
    return data
