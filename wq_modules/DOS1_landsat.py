
# coding: utf-8

#APIs
import os
import numpy as np
import matplotlib.pyplot as plt
import utm
from netCDF4 import Dataset
import datetime

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
        self.thermal_bands = ['B10', 'B11']
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


    def min_band(self):

        self.min_val = {}
        files = os.listdir(self.date_path)

        for f in files:
            if f.endswith('.TIF'):
                name = f.split('.')[0]

                if name.startswith('RT') or name.endswith('BQA') or name.endswith('B8'):
                    continue

                b = plt.imread(os.path.join(self.date_path, f))
                arr = np.asarray(b)
                arr = np.ma.masked_where(arr == 0, arr)
                self.min_val[name.split('_')[-1]] = np.min(arr)


    def Lp(self):

        self.read_metadata()
        self.min_band()

        self.Lp = {}

        for b in self.spectral_bands:

            Lmin = self.metadata['rad']['mult'][b] * self.min_val[b] + self.metadata['rad']['add'][b]
            L1 = 0.01 * (self.metadata['rad']['max'][b] / self.metadata['ref']['max'][b]) * np.cos(self.metadata['AZIMUTH'] * np.pi / 180.)

            self.Lp[b] = Lmin - L1


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


    def read_bands(self):

        self.cut_tiff()

        self.arr_bands = {}

        for band in self.spectral_bands + self.thermal_bands:

            b = plt.imread(os.path.join(self.date_path, '{}.TIF'.format(band)))

            arr = np.asarray(b) # masked array to normal array
    #       arr[arr==0.] = np.nan #replace 0's with Nan's
            arr = np.ma.masked_where(arr == 0, arr)
            self.arr_bands[band] = arr


    def to_reflectance(self):

        self.Lp()
        self.read_bands()

        self.reflectance = {}

        for band in self.spectral_bands:

            r = self.metadata['rad']['mult'][band] * self.arr_bands[band] + self.metadata['rad']['add'][band]
            rad = r - self.Lp[band]

            self.reflectance[band] = rad / ((self.metadata['rad']['max'][band] / self.metadata['ref']['max'][band]) * np.cos(self.metadata['ELEVATION'] * np.pi / 180.))

        for band in self.thermal_bands:

            r = self.metadata["rad"]['mult'][band] * self.arr_bands[band] + self.metadata["rad"]['add'][band]
            self.reflectance[band] = self.metadata["thermal"]["K2"][band] / np.log((self.metadata["thermal"]["K1"][band]/ r) + 1)


    def tiff_to_netcdf(self, band):

        tiff_path = os.path.join(self.date_path, '{}.TIF'.format(band))
        netcdf_path = os.path.join(self.date_path, '{}.nc'.format(band))

        os.system('gdal_translate -of netCDF {} {}'.format(tiff_path, netcdf_path))


    def load_bands(self, band):
        """
        Retrieve a dict of band arrays from a date path
        """

        self.to_reflectance()
        self.tiff_to_netcdf(self.spectral_bands[0])

        band = Dataset(os.path.join(self.date_path, '{}.nc'.format(band)))

        self.latitude = band.variables['y'][:] # latitude array
        self.longitude = band.variables['x'][:] # longitude array


    def create_netCDF(self):
        """
        Sub-function
        Create a NetCDF file with mask: clouds, water, ...
        """

        self.load_bands(self.spectral_bands[0])

        #create de netCDF4 file
        for band in self.spectral_bands + self.thermal_bands:

            ncfile = Dataset(os.path.join(self.date_path, "{}.nc".format(band)),"w", format='NETCDF4_CLASSIC') #'w' stands for write

            ncfile.createDimension('lat', len(self.latitude))
            ncfile.createDimension('lon', len(self.longitude))

            latitude = ncfile.createVariable('lat', 'f4', ('lat',))
            longitude = ncfile.createVariable('lon', 'f4', ('lon',))
            Band1 = ncfile.createVariable('Band1', 'f4', ('lat', 'lon'))

            ncfile.description = "mask"
            ncfile.history = "Created" + datetime.datetime.today().strftime("%m/%d/%Y")
            ncfile.source = "netCDF4 python module"

            latitude[:] = self.latitude
            longitude[:] = self.longitude
            Band1[:,:] = self.reflectance[band]

        ncfile.close
