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

from wq_modules import sentinel as s2
from wq_modules import clouds
from wq_modules import water
from wq_modules import config
from wq_modules import metadata_gen
from wq_modules import meteo
from wq_modules import repos
from wq_modules import config

def get_sentinel2_raw(inidate,enddate,region):
  return s2._init_(inidate,enddate,region)

def cloud_coverage(image):
  return clouds.cloud_coverage(image)

def cloud_mask(image):
  return clouds.cloud_mask(image)

def water_surface(image):
  return water.water_surface(image)

def water_mask(image):
  return water.water_mask(image)

def metadata_gen(title,dateIni,dateEnd,geographicDesc,westBounding,eastBounding,northBounding,southBounding,params):
  return metadata_gen.metadata_gen(title,dateIni,dateEnd,geographicDesc,westBounding,eastBounding,northBounding,southBounding,params)

def get_meteo(inidate,enddate,region):
  return meteo.get_meteo(inidate,enddate,region)

def get_dataset(inidate,enddate,region):
  return repos.get_dataset(inidate,enddate,region)
