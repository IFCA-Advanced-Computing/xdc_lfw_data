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
Given two dates and region, download N Sentinel Collections scenes from ESA 
Sentinel dataHUB.
The downloaded Sentinel collection scenes are compatible with S2MSI1C

Parameters
----------
inidate: datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
enddate: datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
region: name of one reservoir saved in the "coord_reservoirs.json" file

Author: Daniel Garcia
Date: Sep 2018
"""

#imports subfunctions
from wq_modules import config
from wq_modules import utils

#imports apis
import requests
from tqdm import tqdm
import os
import logging
from six.moves.urllib.parse import urljoin
import json

class Sentinel:

    def __init__(self, inidate, enddate, region):

        #data for download files
        self.inidate = inidate.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.enddate = enddate.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.region = region
        self.coord = config.regions[region]["coordinates"]

        #metadata of the data
        self.metadata = {'region': region, # place / reservoir / name of the list
                         'id': config.regions[region]["id"],
                         'coord': config.regions[region]["coordinates"]
                         }

        #work path
        self.path = config.datasets_path

        #landsat credentials
        self.credentials = config.sentinel_pass

        #ESA APIs
        self.api_url = 'https://scihub.copernicus.eu/apihub/'


    def query_date(self):
        """
        query_date
        ----------
        Format datetime input as YYYY-MM-DDThh:mm:ssZ and return it.

        Parameters
        ----------
        in_date : datetime
            datetime.strptime("YYYY-MM-dd", "%Y-%m-%d")
        Returns
        -------
        str
            Formatted string

        Raises
        ------
        ValueError
            Unsupported date value
        """

        return (self.inidate, self.enddate)


    def query_region(self):

        return '"Intersects(POLYGON(({0} {1},{2} {1},{2} {3},{0} {3},{0} {1})))"'.format(self.coord['W'], self.coord['S'], self.coord['E'], self.coord['N'])


    def format_query(self):

        keywords = ["platformname", "beginposition", "footprint", "producttype"]
        query_parts = []

        for k in keywords:
            if k == "platformname":
                query_parts.append('{}:{}'.format(k, "Sentinel-2"))

            if k == "beginposition":

                value = self.query_date()

                # Handle ranged values & Handle value ranges
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    value = '[{} TO {}]'.format(*value)
                else:
                    raise ValueError("Invalid number of elements in list")

                query_parts.append('{}:{}'.format(k, value))

            if k == "footprint":

                coord = self.query_region()
                query_parts.append('{}:{}'.format(k, coord))

            if k == "producttype":

                query_parts.append('{}:{}'.format(k, "S2MSI1C"))

        return ' '.join(query_parts)


    def format_url(self, order_by=None, limit=None, offset=0):


        self.api_url = self.api_url if self.api_url.endswith('/') else self.api_url + '/'
        page_size = 100

        if limit is None:
            limit = page_size
        limit = min(limit, page_size)
        url = 'search?format=json&rows={}'.format(limit)
        url += '&start={}'.format(offset)
        if order_by:
            url += '&orderby={}'.format(order_by)
        return urljoin(self.api_url, url)

    def search(self):
    # store last query (for testing)

        order_by = None
        limit = None
        offset = 0
        query = self.format_query()

        logger = logging.getLogger('sentinelsat.SentinelAPI')
        logger.debug("Sub-query: offset=%s, limit=%s", offset, limit)

        # load query results
        url = self.format_url(order_by, limit, offset)

        session = requests.Session()
        response = session.post(url, {'q': query}, auth=(self.credentials['username'], self.credentials['password']),
                                     headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})

        # parse response content
        try:
            json_feed = response.json()['feed']
            if json_feed['opensearch:totalResults'] is None:
                # We are using some unintended behavior of the server that a null is
                # returned as the total results value when the query string was incorrect.
                print ('Invalid query string. Check the parameters and format.', response)
                print (json_feed['opensearch:totalResults'])
            total_results = int(json_feed['opensearch:totalResults'])
        except (ValueError, KeyError):
            print ('API response not valid. JSON decoding failed.', response)

        products = json_feed.get('entry', [])
        # this verification is necessary because if the query returns only
        # one product, self.products will be a dict not a list
        if isinstance(products, dict):
            products = [products]

        return products, total_results


    def download(self):

        session = requests.session()

        products, total_results = self.search()
        chunk_size = 1024

        session = requests.session()
        session.auth = (self.credentials['username'], self.credentials['password'])

        with open(os.path.join(self.path, 'downloaded_files.json')) as data_file:    
            downloaded_files = json.load(data_file)

        for product in products:

            self.metadata['date'] = (product['summary'].split(',')[0]).split(' ')[-1]
            filename = product['title']
            self.metadata['filename'] = filename

            ID = product['id']
            self.metadata['identifier'] = ID

            if ID in downloaded_files['Sentinel-2'][self.metadata['region']]:
                print ("    file {} already downloaded".format(ID))
                continue

            print ('    Downloading {} files'.format(ID))
            downloaded_files['Landsat 8'][self.region].append(ID)

            #create path and folder for the scene
            date_path = os.path.join(self.path, self.region, ID)
            os.makedirs(date_path)

            #file size
            download_url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('{}')/$value".format(ID)
            resp = session.get(download_url, stream=True, allow_redirects=True)
            total_size = int(resp.headers['content-Length'])

            with tqdm(total=total_size, unit_scale=True, unit='B') as pbar:
                with session.get(download_url, auth =session.auth, stream=True, allow_redirects=True) as r:
                    filename = os.path.join(date_path, '{}.zip'.format(filename))
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(chunk_size)

            utils.unzip_zipfile(filename, date_path)

        # Save the new list of files
        with open(os.path.join(self.path, 'downloaded_files.json'), 'w') as outfile:
            json.dump(downloaded_files, outfile)

        return self.metadata
