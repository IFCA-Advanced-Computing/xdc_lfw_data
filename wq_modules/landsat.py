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
Given two dates and region, download N Landsat Collections scenes from 
EarthExplorer.
The downloaded Landsat collection scenes are compatible with LANDSAT_8_C1

Parameters
----------
inidate: datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
enddate: datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
region: name of one reservoir saved in the "coord_reservoirs.json" file

Author: Daniel Garcia Diaz
Date: Sep 2018
"""

#imports subfunctions
from wq_modules import config
from wq_modules import utils
from wq_modules import DOS1_landsat

#imports apis
import json
import requests
import re
from tqdm import tqdm
import os

class Landsat:

    def __init__(self, inidate, enddate, region=None, action=None):
        """
        initialize the variables used in the landsat class

        Parameters
        ----------
        inidate : str "%Y-%m-%d"
        enddate : str "%Y-%m-%d"
        region : str. e.g: "CdP"
        """

        #data used to download files
        self.inidate = inidate.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.enddate = enddate.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.region = region
        self.coord = config.regions[region]["coordinates"]
        self.action = action
        
        #work path
        self.onedata_mode = config.onedata_mode
        if self.onedata_mode == 1:
            self.path = config.temporal_path
        else:
            self.path = config.datasets_path

        #metadata of the data
        self.output = {}

        #landsat credentials
        self.credentials = config.landsat_pass

        #earth explorer api data
        api_version = '1.4.1'
        self.api_endpoint = 'https://earthexplorer.usgs.gov/inventory/json/v/{}/'.format(api_version)
        self.login_url = 'https://ers.cr.usgs.gov/login/'


    def to_json(self, **kwargs):
        """Convert input arguments to a formatted JSON string
        as expected by the EE API.
        """

        return {'jsonRequest': json.dumps(kwargs)}


    def coordinate(self, latitude, longitude):
        """Coordinate data model.

        Parameters
        ----------
        latitude : float
            Decimal degree coordinate in EPSG:4326 projection.
        longitude : float
            Decimal degree coordinate in EPSG:4326 projection.
        Returns
        -------
        coordinate : dict
            Coordinate data model as a dictionnary.
        """

        return {
            'latitude': latitude,
            'longitude': longitude
        }


    def spatial_filter(self, xmin, ymin, xmax=None, ymax=None):
        """SpatialFilter data model.

        Parameters
        ----------
        xmin : float
            Min. x coordinate (min longitude).
        ymin : float
            Min. y coordinate (min latitude).
        xmax : float, optional
            Max. x coordinate (max longitude).
        ymax : float, optional
            Max. y coordinate (max latitude).

        Returns
        -------
        spatial_filter : dict
            SpatialFilter data model as a dictionnary.
        """

        if not xmax and not ymax:
            xmax = xmin + 0.1
            ymax = ymin + 0.1

        lower_left = self.coordinate(ymin, xmin)
        upper_right = self.coordinate(ymax, xmax)

        return {
            'filterType': 'mbr',
            'lowerLeft': lower_left,
            'upperRight': upper_right
            }


    def temporal_filter(self):
        """TemporalFilter data model.

        Parameters
        ----------
        start_date : str
            ISO 8601 formatted date.
        end_date : str
            ISO 8601 formatted date.

        Returns
        -------
        temporal_filter : dict
            TemporalFilter data model as a dictionnary.
        """

        return {
            'startDate': self.inidate,
            'endDate': self.enddate
        }


    def login(self):
        """Get an API key."""

        data = self.to_json(username=self.credentials["username"], password=self.credentials["password"], catalogID='EE')

        response = requests.post(self.api_endpoint + 'login?', data=data).json()

        if response['error']:
            print ('EE: {}'.format(response['error']))
        return response['data']


    def request(self, request_code, **kwargs):
        """
        Perform a request to the EE API.
        Possible request codes are listed here:
        https://earthexplorer.usgs.gov/inventory/documentation/json-api
        """

        url = self.api_endpoint + request_code

        if 'apiKey' not in kwargs:
            key = self.login()
            kwargs.update(apiKey=key)

        params = self.to_json(**kwargs)
        response = requests.get(url, params=params).json()

        if response['error']:
            print ('EE: {}'.format(response['error']))
        else:
            return response['data']


    def search(self):
        """
        build the query and get the Landsat Collections scenes from request def
        """

        #search parameters
        params = {'datasetName': "LANDSAT_8_C1",
                  'includeUnknownCloudCover': False,
                  'maxResults': 1000
                  }

        #temporal filter
        params.update(temporalFilter=self.temporal_filter())

        #spatial filter
        bbox = (self.coord['W'], self.coord['S'], self.coord['E'], self.coord['N'])
        params.update(spatialFilter=self.spatial_filter(*bbox))

        response = self.request('search', **params)
        scenes = response['results']

        identifiers = []
        for scene in scenes:

            self.acquisitionDate = scene['acquisitionDate']
            self.displayId = scene['displayId']
            self.entityId = scene['entityId']

            #file
            file = scene['displayId'].split('_')
            if file[1] == 'L1TP' and file[-1] == 'T1':
                identifiers.append(scene['entityId'])

        return identifiers


    def _get_tokens(self, body):
        """Get `csrf_token` and `__ncforminfo`."""

        csrf = re.findall(r'name="csrf_token" value="(.+?)"', body)
        ncform = re.findall(r'name="__ncforminfo" value="(.+?)"', body)

        return csrf, ncform


    def download(self):

        session = requests.session()
        rsp = session.get(self.login_url)
        csrf, ncform = self._get_tokens(rsp.text)

        payload = {'username': self.credentials['username'],
                   'password': self.credentials['password'],
                   'csrf_token': csrf,
                   '__ncforminfo': ncform
                   }

        rsp = session.post(self.login_url, data=payload, allow_redirects=False)

        identifiers = self.search()
        chunk_size=1024

        with open(os.path.join(self.path, 'downloaded_files.json')) as data_file:
                downloaded_files = json.load(data_file)

        for ID in identifiers:

            #Metadata file
            self.output[ID] = {}
            self.output[ID]['inidate'] = self.acquisitionDate
            self.output[ID]['enddate'] = self.acquisitionDate
            self.output[ID]['region'] = self.region
            self.output[ID]['W'] = str(self.coord['W'])
            self.output[ID]['E'] = str(self.coord['E'])
            self.output[ID]['N'] = str(self.coord['N'])
            self.output[ID]['S'] = str(self.coord['S'])
            self.output[ID]['params'] = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
            
            if ID in downloaded_files['Landsat 8'][self.region]:
                print ("    file {} already downloaded".format(ID))
                continue
            
            #create path and folder for the scene
            date_path = os.path.join(self.path, self.region, ID)
            self.output[ID]['path'] = date_path
            os.makedirs(date_path)

            print ('    Downloading {} files'.format(ID))
            downloaded_files['Landsat 8'][self.region].append(ID)

            #file size
            band_url = 'https://earthexplorer.usgs.gov/download/12864/{}/STANDARD/EE'.format(ID)
            resp = session.get(band_url, stream=True, allow_redirects=True)
            total_size = int(resp.headers['content-Length'])

            #download
            with tqdm(total=total_size, unit_scale=True, unit='B') as pbar:
                with session.get(band_url, stream=True, allow_redirects=True) as r:
                    filename = r.headers['Content-Disposition'].split('=')[-1]
                    filename = os.path.join(date_path, filename)
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(chunk_size)

            #preprocess data
            utils.unzip_tarfile(filename, date_path)
            d = DOS1_landsat.DOS1(date_path, self.region)
            d.create_netCDF()

        # Save the new list of files
        with open(os.path.join(self.path, 'downloaded_files.json'), 'w') as outfile:
            json.dump(downloaded_files, outfile)
