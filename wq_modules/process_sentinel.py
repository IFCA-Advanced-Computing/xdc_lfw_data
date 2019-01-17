#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 16:53:08 2019

@author: dani
"""

import os
import utm

#imports subfunctions
from wq_modules import config

class preprocess_sentinel:

    def __init__(self, date_path, region):
        """
        initialize the variables used to preprocess sentinel images
        """

        self.date_path = date_path
        self.region = region
        self.coord = config.regions[self.region]["coordinates"]

    def path(self):

        for root, dirs, files in os.walk(self.date_path):
            for name in files:
                if name.endswith('B01.jp2'):
                    root_path = root

        return root_path

    def jp2_to_tiff_and_cut(self):

        up_left = utm.from_latlon (self.coord['N'], self.coord['W'])
        down_right = utm.from_latlon (self.coord['S'], self.coord['E'])

        root_path = self.path()
        files = os.listdir(root_path)

        for f in files:

            jp2_path = os.path.join(root_path, f)

            name = (f.split('.')[0]).split('_')[-1]
            tiff_path = os.path.join(self.date_path, '{}.TIF'.format(name))

            os.system("gdal_translate -of GTiff -projwin {} {} {} {} {} {}".format(up_left[0], up_left[1], down_right[0], down_right[1], jp2_path, tiff_path))

    def tiff_to_netcdf(self):

        self.jp2_to_tiff_and_cut()

        files = os.listdir(self.date_path)

        for f in files:
            if f.endswith('.TIF'):

                band = f.split('.')[0]

                tiff_path = os.path.join(self.date_path, '{}.TIF'.format(band))
                netcdf_path = os.path.join(self.date_path, '{}.nc'.format(band))

                os.system('gdal_translate -of netCDF {} {}'.format(tiff_path, netcdf_path))
