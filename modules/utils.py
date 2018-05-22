"""
Satellite utils

Author: Daniel García
Date: May 2018
"""
import requests, zipfile
import imageio
import shutil
import io
import os
from netCDF4 import Dataset
import json

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

def metadata_sentinel_file(sat_list):
    """
    create a file with the metadata
    """
    sentinel_metadata = {'id': sat_list.getInfo()[0]['id'],
                          'file': sat_list.getInfo()[0]['properties']['DATATAKE_IDENTIFIER'],
                          'cloud_coverage': sat_list.getInfo()[0]['properties']['CLOUD_COVERAGE_ASSESSMENT'],
                          'SENSING_ORBIT_DIRECTION': sat_list.getInfo()[0]['properties']['SENSING_ORBIT_DIRECTION']
                        }
    return sentinel_metadata

def metadata_landsat_file(sat_list):
    """
    create a file with the metadata
    """
    metadata_raw_files = {'id': sat_list.getInfo()[0]['id'],
                          'date': sat_list.getInfo()[0]['properties']['DATE_ACQUIRED'],
                          'cloud_coverage': sat_list.getInfo()[0]['properties']['CLOUD_COVER'],
                          'category': sat_list.getInfo()[0]['properties']['COLLECTION_CATEGORY']
                        }
    return metadata_raw_files

#def downloaded_data_file(datasets_path):
#    try:
#        with open(os.path.join(datasets_path, 'files.json')) as data_file:    
#            json.load(data_file)
#    except:
#        reservoir_dict = {"Sentinel-2": {"CdP": [], "Sanabria": [], "Castro de las Cogotas": []},
#                          "Landsat 8": {"CdP": [], "Sanabria": [], "Castro de las Cogotas": []}}
#        with open(os.path.join(datasets_path, 'files.json'), 'w') as outfile:
#                json.dump(reservoir_dict, outfile)