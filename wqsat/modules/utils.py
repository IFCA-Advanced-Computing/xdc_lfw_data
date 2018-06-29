"""
Satellite utils

Author: Daniel Garcia
Date: May 2018
"""
import requests, zipfile
import imageio
import shutil
import io
import os
from netCDF4 import Dataset
import json
import datetime as dt
import numpy as np

def download_zip(zip_file_url, output_path):
    """
    Sub-function used on: get_sentinel2_raw() and get_landsat8_raw()
    Download and unzip the earth engine data with the url of the file
    Inputs:
        zip_file_url : earth engine url of file
        output_path : path to download and save
    """
    r = requests.get(zip_file_url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(output_path)
    
def tiff_to_netCDF(files_path):
    """
    Sub-function used on: get_sentinel2_raw() and get_landsat8_raw()
    Transform GTIFF files (bands of satellite) to netCDF 
    Inputs:
        files_path: path of the folder that contains the files
    """
    files = os.listdir(files_path)
    for f in files:
        file_path = os.path.join(files_path, f)
                
        if f.endswith('.tif'):
                    
            #Transform tif to netcdf file
            band_name = f.split('.')[-2]
            netcdf_path = os.path.join(files_path, '{}.nc'.format(band_name))
            os.system('gdal_translate -of netCDF {} {}'.format(file_path, netcdf_path))                
                
        os.remove(file_path)
    
def create_netCDF(path, mask, lat, lon):
    """
    Sub-function used on: cloud.cloud_mask.
    Create a NetCDF file with mask_cloud
    """
    #create de netCDF4 file
    ncfile = Dataset(os.path.join(path, "Cloud.nc"),"w", format='NETCDF4_CLASSIC') #'w' stands for write
        
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
    Band1[:,:] = np.ones((len(lat), len(lon))) * mask * 255
    
    ncfile.close    

def check_corner(image, date_path, query_dict):
    """
    Download sample to check if it is a corner, and therefore the image is unusable.
    """
    band = image.select('B1')
    band_url = band.getDownloadURL(query_dict)
    download_zip(band_url, date_path)
    
    tif_file = [f for f in  os.listdir(date_path) if f.endswith('.tif')]
    arr = imageio.imread(os.path.join(date_path, tif_file[0]))
    corner = False
    if (arr == 0).any():
        corner = True
    shutil.rmtree(date_path, ignore_errors=True)        
    
    return corner 

def load_bands(datepath, band_list):
    """
    Retrieve a dict of band arrays from a date path
    """
    band_dict = {}
    for b in band_list:
        band = Dataset(os.path.join(datepath, '{}.nc'.format(b)))
        band_dict[b] = band.variables['Band1'][:] # band array
    
    latitude = band.variables['lat'][:] # latitude array
    longitude = band.variables['lon'][:] # longitude array
    return band_dict, latitude, longitude

def metadata_file(mission, sat_list):
    """
    create a file with the metadata
    """
    if mission == 'Sentinel-2':
        metadata = {'id': sat_list.getInfo()[0]['id'],
                    'file': sat_list.getInfo()[0]['properties']['DATATAKE_IDENTIFIER'],
                    'cloud_coverage': sat_list.getInfo()[0]['properties']['CLOUD_COVERAGE_ASSESSMENT'],
                    'SENSING_ORBIT_DIRECTION': sat_list.getInfo()[0]['properties']['SENSING_ORBIT_DIRECTION']
                    }
    elif mission == 'Landsat8':
        metadata = {'id': sat_list.getInfo()[0]['id'],
                    'date': sat_list.getInfo()[0]['properties']['DATE_ACQUIRED'],
                    'cloud_coverage': sat_list.getInfo()[0]['properties']['CLOUD_COVER'],
                    'category': sat_list.getInfo()[0]['properties']['COLLECTION_CATEGORY']
                    }
    return metadata

def check_file(path):
    try:
        with open(os.path.join(path, 'downloaded_files.json')) as data_file:    
            json.load(data_file)
    except:
        os.mkdir(path)
        dictionary = {"Sentinel-2": {"CdP": [], "Sanabria": [], "Castro de las Cogotas": []},
                    "Landsat 8": {"CdP": [], "Sanabria": [], "Castro de las Cogotas": []}}
        with open(os.path.join(path, 'downloaded_files.json'), 'w') as outfile:                
            json.dump(dictionary, outfile)