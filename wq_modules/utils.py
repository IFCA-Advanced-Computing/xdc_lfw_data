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
Satellite utils

Author: Daniel Garcia Diaz
Date: May 2018
"""

#Submodules
from wq_modules import config
from wq_modules import metadata_gen

#APIs
import zipfile, tarfile
import argparse
import numpy as np
import os, shutil
import json
import datetime
import utm
from netCDF4 import Dataset
from six import string_types


def valid_date(sd, ed):
    """
    check if the format date input is string("%Y-%m-%d") or datetime.date
    and return it as format datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")

    Parameters
    ----------
    sd(start_date) : str "%Y-%m-%d"
    ed(end_date) : str "%Y-%m-%d"

    Returns
    -------
    sd : datetime
        datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
    ed : datetime
        datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")

    Raises
    ------
    FormatError
        Unsupported format date
    ValueError
        Unsupported date value
    """

    if isinstance(sd, datetime.date) and isinstance(ed, datetime.date):

        return sd, ed

    elif isinstance(sd, string_types) and isinstance(ed, string_types):    
        try:
            sd = datetime.datetime.strptime(sd, "%Y-%m-%d")
            ed = datetime.datetime.strptime(ed, "%Y-%m-%d")
            if sd < ed:
                return sd, ed
            else:
                msg = "Unsupported date value: '{} or {}'.".format(sd, ed)
                raise argparse.ArgumentTypeError(msg)
        except:
            msg = "Unsupported format date: '{} or {}'.".format(sd, ed)
            raise argparse.ArgumentTypeError(msg)
    else:
        msg = "Unsupported format date: '{} or {}'.".format(sd, ed)
        raise argparse.ArgumentTypeError(msg)


def valid_region(r):
    """
    check if the regions exits

    Parameters
    ----------
    r(region) : str e.g: "CdP"

    Raises
    ------
    FormatError
            Not a valid region
    """

    if r in config.regions:
        pass
    else:
        msg = "Not a valid region: '{0}'.".format(r)
        raise argparse.ArgumentTypeError(msg)


def valid_action(a):
    """
    check if the action exits in the list of keywords

    Parameters
    ----------
    a(action) : str e.g: "cloud_mask"

    Raises
    ------
    FormatError
            Not a valid action
    """

    if a in config.keywords:
        pass
    else:
        msg = "Not a valid action: '{0}'.".format(a)
        raise argparse.ArgumentTypeError(msg)


def path_configurations(onedata_mode):
    """
    Configure the tree of datasets path depend of onedata mode. 
    Create the folder and the downloaded_files file.

    Parameters
    ----------
    path : datasets path from config file
    """

    file = 'downloaded_files.json'
    list_region = config.regions

    if onedata_mode == 1:

        onedata_path = config.datasets_path
        local_path = config.local_path
        if not (os.path.isdir(local_path)):
            os.mkdir(local_path)

        for region in list_region:
            region_path = os.path.join(local_path, region)
            if not (os.path.isdir(region_path)):
                os.mkdir(region_path)

        shutil.copy(os.path.join(onedata_path, file), local_path)

    else:

        local_path = config.local_path

        try:
            with open(os.path.join(local_path, file)) as data_file:
                json.load(data_file)
        except:
            if not (os.path.isdir(local_path)):
                os.mkdir(local_path)

            dictionary = {"Sentinel-2": {}, "Landsat 8": {}}

            for region in list_region:

                os.mkdir(os.path.join(local_path, region))
                dictionary['Sentinel-2'][region] = []
                dictionary['Landsat 8'][region] = []

            with open(os.path.join(local_path, 'downloaded_files.json'), 'w') as outfile:
                json.dump(dictionary, outfile)


def unzip_tarfile(local_filename, date_path):

    tar = tarfile.open(local_filename, "r:gz")
    tar.extractall(path = date_path)
    tar.close()
    os.remove(local_filename)


def unzip_zipfile(local_filename, date_path):

    zip_ref = zipfile.ZipFile(local_filename, 'r')
    zip_ref.extractall(date_path)
    zip_ref.close()
    os.remove(local_filename)


def to_onedata(files, region):

    #paths
    onedata_path = config.datasets_path

    for file in files:

        try:
            date_path = files[file]['path']

            print ("    moving {} file to onedata".format(file))
            shutil.move(date_path, os.path.join(onedata_path, region))
            metadata_gen.metadata_gen(file, files[file]['inidate'], files[file]['enddate'], files[file]['region'], files[file]['N'], files[file]['W'], files[file]['params'])

            shutil.rmtree(date_path, ignore_errors=True)

        except:
            continue


def clean_temporal_path():

    #path
    onedata_path = config.datasets_path
    local_path = config.local_path
    file = 'downloaded_files.json'

    shutil.copy(os.path.join(local_path, file), onedata_path)
    shutil.rmtree(local_path, ignore_errors=True)


def load_bands(datepath, band_list):
    """
    Retrieve a dict of band arrays from a date path
    """
    band_dict = {}
    for b in band_list:
        band = Dataset(os.path.join(datepath, '{}.nc'.format(b)))
        band_dict[b] = band.variables['Band1'][:] # band array

        if 'lat' in band.variables:

            latitude = band.variables['lat'][:] # latitude array
            longitude = band.variables['lon'][:] # longitude array

        elif 'y' in band.variables:
            latitude = band.variables['y'][:] # latitude array
            longitude = band.variables['x'][:] # longitude array

        else:
            msg = "NetCDF damaged or impossible to read"
            raise argparse.ArgumentTypeError(msg)


    return longitude, latitude, band_dict


def cut_tiff_image(date_path, region):

    coord = config.regions[region]['coordinates']

    up_left = utm.from_latlon (coord['N'], coord['W'])
    down_right = utm.from_latlon (coord['S'], coord['E'])

    files = os.listdir(date_path)
    for f in files:
        if f.endswith('.TIF'):

            band_path = os.path.join(date_path, f)

            band = f.split('_')[-1]
            new_band_path = os.path.join(date_path, band)

            os.system('gdal_translate -projwin {} {} {} {} {} {}'.format(up_left[0], up_left[1], down_right[0], down_right[1], band_path, new_band_path))

            if os.path.isfile(new_band_path):
                os.remove(band_path)


def tiff_to_netcdf(date_path):

    files = os.listdir(date_path)
    for f in files:
        if f.endswith('.TIF'):
            band_path = os.path.join(date_path, f)

            name = f.split('.')[0]
            netcdf_path = os.path.join(date_path, '{}.nc'.format(name))

            os.system('gdal_translate -of netCDF {} {}'.format(band_path, netcdf_path))

            if os.path.isfile(netcdf_path):
                os.remove(band_path)


def create_netCDF(path, mask, lat, lon, name):
    """
    Sub-function used on: cloud.cloud_mask & water.water_mask
    Create a NetCDF file with mask: clouds, water, ...
    """
    #create de netCDF4 file
    ncfile = Dataset(os.path.join(path, "{}.nc".format(name)),"w", format='NETCDF4_CLASSIC') #'w' stands for write

    ncfile.createDimension('lat', len(lat))
    ncfile.createDimension('lon', len(lon))

    latitude = ncfile.createVariable('lat', 'f4', ('lat',))
    longitude = ncfile.createVariable('lon', 'f4', ('lon',))  
    Band1 = ncfile.createVariable('Band1', 'f4', ('lat', 'lon'))

    ncfile.description = "mask"
    ncfile.history = "Created" + datetime.datetime.today().strftime("%m/%d/%Y")
    ncfile.source = "netCDF4 python module"

    latitude[:] = lat
    longitude[:] = lon
    Band1[:,:] = mask

    ncfile.close


def get_pixel_area(longitude, latitude):
    """
    Compute the new pixel area after the lat_long --> meters conversion
    """

    scale_x = np.mean(longitude[1:] - longitude[:-1])
    scale_y = np.mean(latitude[1:] - latitude[:-1])
    return scale_x * scale_y


def onedata(region, temporal_path, metadata):
    """
    Move the data from temporal folder to onedate after the preprocessing
    """

    onedata_path = config.datasets_path
    region_path = os.path.join(onedata_path, region)

    for file in metadata:
        file_path = os.path.join(temporal_path, file)
        if os.path.isdir(file_path):
            shutil.move(file_path, region_path)
