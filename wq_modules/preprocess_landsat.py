
# coding: utf-8

#APIs
import os
import numpy as np
import utm
from netCDF4 import Dataset
import datetime
import gdal

#imports subfunctions
from wq_modules import config

class DOS1:

    def __init__(self, date_path, region):
        """
        initialize the variables used to preprocess landsat images
        and apply DOS1 atmospheric correction
        """

        self.date_path = date_path
        self.region = region
        self.spectral_bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B9']
        self.coord = config.regions[self.region]["coordinates"]


    def read_metadata(self):

        self.metadata = {"rad":{"max":{}, "min":{}, "mult":{}, "add":{}}, "ref":{"max":{}, "min":{}, "mult": {}, "add": {}}, "thermal":{"K1":{}, "K2":{}}}
        files = os.listdir(self.date_path)

        for f in files:
            if f.endswith('MTL.txt'):
                textfile = f

        with open(os.path.join(self.date_path, textfile)) as infile:
            for line in infile:
                if line.startswith("    EARTH"):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[1] + '_' + l[0].split('_')[2]
                    name = name.replace(' ', '')

                    self.metadata[name] = value

                elif line.startswith('    SUN'):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[1]
                    name = name.replace(' ', '')

                    self.metadata[name] = value

                elif line.startswith("    RADIANCE"):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[-2][0] + l[0].split('_')[-1]
                    name = name.replace(' ', '')

                    if l[0].split('_')[1] == "MAXIMUM":
                        self.metadata["rad"]["max"][name] = value
                    elif l[0].split('_')[1] == "MINIMUM":
                        self.metadata["rad"]["min"][name] = value
                    elif l[0].split('_')[1] == "MULT":
                        self.metadata["rad"]["mult"][name] = value
                    elif l[0].split('_')[1] == "ADD":
                        self.metadata["rad"]["add"][name] = value

                elif line.startswith("    REFLECTANCE"):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[-2][0] + l[0].split('_')[-1]
                    name = name.replace(' ', '')

                    if l[0].split('_')[1] == "MAXIMUM":
                        self.metadata["ref"]["max"][name] = value
                    elif l[0].split('_')[1] == "MINIMUM":
                        self.metadata["ref"]["min"][name] = value
                    elif l[0].split('_')[1] == "MULT":
                        self.metadata["ref"]["mult"][name] = value
                    elif l[0].split('_')[1] == "ADD":
                        self.metadata["ref"]["add"][name] = value

                elif line.startswith("    K1_CONSTANT"):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[-2][0] + l[0].split('_')[-1]
                    name = name.replace(' ', '')

                    self.metadata["thermal"]["K1"][name] = value

                elif line.startswith("    K2_CONSTANT"):

                    l = line.split('=')
                    value = float(l[-1])
                    name = l[0].split('_')[-2][0] + l[0].split('_')[-1]
                    name = name.replace(' ', '')

                    self.metadata["thermal"]["K2"][name] = value


    def cut_tiff(self):

        up_left = utm.from_latlon (self.coord['N'], self.coord['W'])
        down_right = utm.from_latlon (self.coord['S'], self.coord['E'])

        files = os.listdir(self.date_path)
        for f in files:
            if f.endswith('.TIF'):
                name = f.split('.')[0]

                if name.startswith('RT') or name.endswith('BQA') or name.endswith('B8'):
                    continue

                old_tiff = os.path.join(self.date_path, f)

                band = '{}.TIF'.format(name.split('_')[-1])
                new_tiff = os.path.join(self.date_path, band)

                os.system('gdal_translate -projwin {} {} {} {} {} {}'.format(up_left[0], up_left[1], down_right[0], down_right[1], old_tiff, new_tiff))


    def tiff_to_netcdf(self, band):

        tiff_path = os.path.join(self.date_path, '{}.TIF'.format(band))
        netcdf_path = os.path.join(self.date_path, '{}.nc'.format(band))

        os.system('gdal_translate -of netCDF {} {}'.format(tiff_path, netcdf_path))


    def load_bands(self, band):
        """
        Retrieve a dict of band arrays from a date path
        """

        self.cut_tiff()
        self.tiff_to_netcdf(self.spectral_bands[0])

        band = Dataset(os.path.join(self.date_path, '{}.nc'.format(band)))

        self.latitude = band.variables['y'][:] # latitude array
        self.longitude = band.variables['x'][:] # longitude array


    def dos1(self, arr_band, band):

        #calculate the path radiance
        minimun = np.amin(arr_band)
        Lmin = self.metadata['rad']['mult'][band] * minimun + self.metadata['rad']['add'][band]
        L1 = 0.01 * (self.metadata['rad']['max'][band] / self.metadata['ref']['max'][band]) * np.cos(self.metadata['AZIMUTH'] * np.pi / 180.)
        Lp = Lmin - L1

        #calculate the radiance
        r = self.metadata['rad']['mult'][band] * arr_band + self.metadata['rad']['add'][band]
        rad = r - Lp

        #land surface reflectance
        sr_arr = np.pi*(rad)*(self.metadata['SUN_DISTANCE']**2) / (np.pi*(self.metadata['SUN_DISTANCE']**2)*self.metadata['rad']['max'][band] / self.metadata['ref']['max'][band])

        return sr_arr


    def create_netCDF(self, sr_arr, band):
        """
        Sub-function
        Create a NetCDF file with mask: clouds, water, ...
        """

        ncfile = Dataset(os.path.join(self.date_path, "{}.nc".format(band)),"w", format='NETCDF4_CLASSIC') #'w' stands for write
        ncfile.description = "mask"

        ncfile.createDimension('lat', len(self.latitude))
        ncfile.createDimension('lon', len(self.longitude))

        latitude = ncfile.createVariable('lat', np.float32, ('lat',))
        longitude = ncfile.createVariable('lon', np.float32, ('lon',))
        Band1 = ncfile.createVariable('Band1', np.float32, ('lat', 'lon'))

        ncfile.history = "Created" + datetime.datetime.today().strftime("%m/%d/%Y")
        ncfile.source = "netCDF4 python module"

        # Variable Attributes
        latitude.units = 'meters_north'
        longitude.units = 'meters_east' 

        latitude[:] = self.latitude
        longitude[:] = self.longitude
        Band1[:,:] = sr_arr

        ncfile.close()


    def to_reflectance(self):

        self.read_metadata()
        self.load_bands(self.spectral_bands[0])

        for band in self.spectral_bands:

            file_path = os.path.join(self.date_path, '{}.TIF'.format(band))
            ds = gdal.Open(file_path)
            arr = np.array(ds.GetRasterBand(1).ReadAsArray())

            sr_arr = self.dos1(arr, band)
            self.create_netCDF(sr_arr, band)
