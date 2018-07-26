from wq_modules import sentinel2 as s2
from wq_modules import clouds
from wq_modules import water
from wq_modules import config
from wq_modules import metadata_gen
from wq_modules import meteo
from wq_modules import config
from wq_modules import tasks

def get_sentinel2_raw(inidate,enddate,region):
    return s2.get_sentinel2_raw(inidate,enddate,region)

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
    return get_meteo(inidate,enddate,region)
