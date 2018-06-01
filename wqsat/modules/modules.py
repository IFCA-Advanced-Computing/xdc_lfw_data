from . import sentinel2 as s2
from . import clouds
from . import water
from . import config
from . import metadata_gen
from . import meteo
from . import config

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
