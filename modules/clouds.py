#TODO
#imports here

import os
import json
import numpy as np
from netCDF4 import Dataset
import datetime as dt

from . import utils
from . import config 

def cloud_coverage(region, files):
    """ Given a satellite image, returns the cloud covarage
        image: file
    """
    datasets_path = config.satelite_info['data_path']
    
    #create csv data(headers)
    csv_headers = ['file', 'cloud_coverage']
    csv_data =[csv_headers]
    
    reservoir_path = os.path.join(datasets_path, region)
    #find cloud coverage in metadata
    for f in files:
        dir_path = os.path.join(reservoir_path, f)

        with open(os.path.join(dir_path, '{}.json'.format(f))) as data_file:    
            metadata_file = json.load(data_file)
        cloud_coverage = metadata_file['cloud_coverage']
        
        #create csv row
        row = [f, cloud_coverage]
        csv_data.append(row)

    #save csv file
    np.savetxt(os.path.join(reservoir_path, '{}.csv'.format(region)), csv_data, fmt='%s', delimiter=",")


def sentinel_cloud_mask(region, files):
    """ Given a satellite image, returns the cloud mask
        image: netCDF file
    """
    datasets_path = config.satelite_info['data_path']
    
    #check if the cloud mask already done
    for f in files:
        date_path = os.path.join(datasets_path, region, f)
        if 'Cloud.nc' in os.listdir(date_path):
            continue
    
        band_list = ['B3', 'B4', 'B11']
        bands, lat, lon = utils.load_bands(date_path, band_list)
    
        # Divide values by 10000 if bands downloaded from Google Earth API
        for k, v in bands.items():
            bands[k] = v / 10000.
    
        ndsi = (bands['B3'] - bands['B11']) / (bands['B3'] + bands['B11']) #vegetation index
    
        #filters to discriminate clouds
        mask_potential_cloud = (bands['B4'] > 0.07) * (bands['B4'] < 0.25) # are passed to Step 1.b 
        mask_cloud = bands['B4'] > 0.25 # Clouds , are passed to step2
        mask_cloud = mask_cloud + (mask_potential_cloud * (ndsi > -0.16)) # are passed to Step 2
        
        #create de netCDF4 file
        ncfile = Dataset(os.path.join(date_path, "Cloud.nc"),"w", format='NETCDF4_CLASSIC') #'w' stands for write
        
        ncfile.createDimension('lat', len(lat))
        ncfile.createDimension('lon', len(lon))
        
        latitude = ncfile.createVariable('lat', 'f4', ('lat',))
        longitude = ncfile.createVariable('lon', 'f4', ('lon',))  
        Band1 = ncfile.createVariable('Band1', 'f4', ('lat', 'lon'))
        
        ncfile.description = "mask of clouds"
        ncfile.history = "Created" + dt.datetime.today().strftime("%m/%d/%Y")
        ncfile.source = "netCDF4 python module"
        
        latitude[:] = lat
        longitude[:] = lon
        Band1[:,:] = np.ones((len(lat), len(lon))) * mask_cloud * 255
    
        ncfile.close


def landsat_cloud_mask(region, files):
    """ Given a satellite image, returns the cloud mask
        image: netCDF file
    """
    datasets_path = config.satelite_info['data_path']
    
    #check if the cloud mask already done
    for f in files:
        date_path = os.path.join(datasets_path, region, f)
        if 'Cloud.nc' in os.listdir(date_path):
            continue
        
        band_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        bands, lat, lon = utils.load_bands(date_path, band_list)
        
        #Clouds
        cloud = ((bands['B1'] > 0.18) & (bands['B5'] > 0.14) & (np.max((bands['B1'], bands['B3'])) > bands['B5'] * 0.67))
        
        #create de netCDF4 file
        ncfile = Dataset(os.path.join(date_path, "Cloud.nc"),"w", format='NETCDF4_CLASSIC') #'w' stands for write
        
        ncfile.createDimension('lat', len(lat))
        ncfile.createDimension('lon', len(lon))
        
        latitude = ncfile.createVariable('lat', 'f4', ('lat',))
        longitude = ncfile.createVariable('lon', 'f4', ('lon',))  
        Band1 = ncfile.createVariable('Band1', 'f4', ('lat', 'lon'))
        
        ncfile.description = "mask of clouds"
        ncfile.history = "Created" + dt.datetime.today().strftime("%m/%d/%Y")
        ncfile.source = "netCDF4 python module"
        
        latitude[:] = lat
        longitude[:] = lon
        Band1[:,:] = np.ones((len(lat), len(lon))) * cloud * 255
    
        ncfile.close
