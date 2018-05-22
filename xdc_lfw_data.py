import argparse
import datetime
from modules import sentinel2
from modules import landsat8
from modules import clouds
from modules import water

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%d-%m-%Y").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Gets data from satellite')

parser.add_argument("-sd", 
                    "--startdate", 
                    help="The Start Date - format DD-MM-YYYY",
                    required=True,
                    dest='start_date',
                    type=valid_date)

parser.add_argument("-ed", 
                    "--enddate", 
                    help="The Start Date - format DD-MM-YYYY",
                    required=True,
                    dest='end_date',
                    type=valid_date)

parser.add_argument('--region', 
                    dest='region',
                    required=True,
                    choices=['CdP','Sanabria','Cogotas'],
                    help='Valid values: CdP, Sanabria, Cogotas')

parser.add_argument('--action',
                    dest='action',
                    required=False,
                    choices=['cloud_coverage','cloud_mask','water_surface', 'water_mask'],
                    help='Valid values: cloud_coverage, cloud_mask, water_surface, water_mask')

parser.add_argument('--param',
                    dest='param',
                    required=False,
                    choices=['chl', 'turbidity'],
                    help='Valid values: chl, turbidity')

args = parser.parse_args()

#TODO Check end_date > start_date

#TODO Check region to attach coordinates

#Action management
if args.action is not None:
    if args.action == 'cloud_coverage':

        sentinel_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        landsat_img = landsat8.get_landsat8_raw(args.start_date,args.end_date,args.region)

        list_files = sentinel_img+landsat_img
        cloud_cov = clouds.cloud_coverage(args.region, list_files)

        print(cloud_cov)

    elif args.action == 'cloud_mask':

        sentinel_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        cloud_mask = clouds.sentinel_cloud_mask(args.region, sentinel_img)

        landsat_img = landsat8.get_landsat8_raw(args.start_date,args.end_date,args.region)
        cloud_mask = clouds.landsat_cloud_mask(args.region, landsat_img)

        print(cloud_mask)

    elif args.action == 'water_surface':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        water_sur = water.water_surface(sat_img)
        print(water_sur)
    elif args.action == 'water_mask':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        water_mask = water.water_mask(sat_img)
        print(water_mask)
