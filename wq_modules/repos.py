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

import requests
import json
import csv
from datetime import datetime
import xml.etree.cElementTree as ET
from wq_modules import metadata_gen
from wq_modules import config

def get_oai_metadata_formats(url):
    """Lists the available metadata formats
        Parameters
        ----------
        url : string
            OAI-PMH endpoint url
        Returns
        -------
        metadata_formats : 
            Name of the downloaded file(s).
    """
    metadata_formats = []
    oai_verb = '?verb=ListMetadataFormats'
    oai = requests.get(url + oai_verb) #Peticion al servidor
    xmlTree = ET.ElementTree(ET.fromstring(oai.text))
    iterator = xmlTree.iter()
    for elem in iterator:
        if (elem.tag == '{http://www.openarchives.org/OAI/2.0/}metadataPrefix'):
            metadata_formats.append(elem.text)
    return metadata_formats

def search_dataset(url,oai_set,metadata_format):
    """Search the datasets identifiers in the defined set
        Parameters
        ----------
        url : string
            OAI-PMH endpoint url
        oai_set : string
            OAI-PMH set where the datasets will be searched
        metadata_format : string
            Selected metadata format to search
        Returns
        -------
        dataset_ids : array 
            Dataset IDs
    """
    #Define bounds to search in specific set
    bounds = "&set="+oai_set
    oai = requests.get(url+'?verb=ListRecords&metadataPrefix='+metadata_format+bounds)

    oaiTree = ET.ElementTree(ET.fromstring(oai.text.encode('utf-8')))
    item = oaiTree.findall('.//{http://datacite.org/schema/kernel-3}identifier')
    return item
    
def check_dataset(ids,api_url,start_date,end_date,region,dataset_path):
    """Checks if the available datasets satisfy the dates and location req
        Parameters
        ----------
        ids : array
            List of dataset ids
        api_url : string
            API to get dataset metadata
        start_date : datetime
            Start date time to search the dataset
        end_date : datetime
            End date time to search the dataset
        location : string
            Region to get the data from
        Returns
        -------
        downloaded_datasets : array 
            List of downloaded datasets
    """
    file_list = []
    for i in ids:
        headers = {'accept': 'application/json'}
        #TODO Manage different types of identifiers (i.text.replace('record', 'api/records'),headers))
        r = requests.get('https://doi.org/'+i.text,headers)
        r = requests.get(r.url.replace('record', 'api/records'),headers)
        beginDate=''
        endDate=''
        location=''
        try:
            for o in r.json()['metadata']['keywords']:
                if 'beginDate' in o:
                    beginDate = o.rsplit(":",1)[1].replace("'","")
                    print(beginDate)
                if 'endDate' in o:
                    endDate = o.rsplit(":",1)[1].replace("'","")
                    print(endDate)
                if 'location' in o:
                    location = o.rsplit(":",1)[1].replace("'","")
                    print(location)
        except:
            print("No Keywords or any other shit")

        if len(beginDate) > 0 and datetime.strptime(beginDate, "%Y-%m-%d") <= start_date and len(endDate) > 0 and datetime.strptime(endDate, "%Y-%m-%d") >= end_date and len(location) > 0 and location == region:
            for u in r.json()['files']:
                if u['type'] == 'csv':
                    print(u['links']['self'])
                    link = u['links']['self']
                    file_name = dataset_path + "_" + u["key"]
                    with open(file_name, "wb") as f:
                        print("Downloading %s" % file_name)
                        response = requests.get(link, stream=True)
                        total_length = response.headers.get('content-length')

                        if total_length is None: # no content length header
                            f.write(response.content)
                        else:
                            dl = 0
                            total_length = int(total_length)
                            for data in response.iter_content(chunk_size=4096):
                                dl += len(data)
                                f.write(data)
                                done = int(50 * dl / total_length)
                                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                                sys.stdout.flush()
                    file_list.append(file_name)
                    print("Download complete")     
                    #Get Latitude, Longitude
                    coords = config.regions['regions'][region]
                    lon = 0
                    for l in coords:
                        lon = lon + l[0]
                        lon = lon/len(coords)
                        lat = 0
                    for l in coords:
                        lat = lat + l[1]
                        lat = lat/len(coords)
                    print("Lat: %s Lon: %s" % (lat,lon))
                                
                    #Metadata attachment
                    #TODO add wind, prec
                    print("Attaching Metadata")
                    metadata_gen.metadata_gen(file_name,beginDate,endDate,region,str(lat),str(lon),["Just","a","Test"])
    return file_list
def get_dataset(start_date, end_date, region):
    """Coordinate data model.
        Parameters
        ----------
        start_date : datetime
            Start date time to search the dataset
        end_date : datetime
            End date time to search the dataset
        location : string
            Region to get the data from
        Returns
        -------
        output : json
            Name of the downloaded file(s).
    """
    #onedata mode
    if (config.onedata_mode == 1):
        datasets_path = '/onedata/' + config.onedata_user + '/' + config.onedata_space + '/' + config.download_datasets
    else:
        datasets_path = '.' + config.download_datasets
   
    general_name = datasets_path + '/' + region + '/' + "dataset_"+start_date.strftime('%Y-%m-%d')+"_"+end_date.strftime('%Y-%m-%d')

    #Searching datasets OAI-PMH
    print("Searching datasets OAI-PMH")
    oai_url = 'https://zenodo.org/oai2d'
    metadata_formats = get_oai_metadata_formats(oai_url) 

    #TODO hardcoded
    print("Searching Datasets")
    oai_set = 'user-cdp'
    dataset_list = search_dataset(oai_url,oai_set,'oai_datacite')    

    print("Checking/download Datasets")
    api_url = 'https://doi.org/'
    file_list = check_dataset(dataset_list,api_url,start_date,end_date,region,datasets_path)

    return {"output": file_list}
