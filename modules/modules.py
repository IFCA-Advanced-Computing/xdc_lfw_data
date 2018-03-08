from . import sentinel2 as s2
from . import clouds
from . import water

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
