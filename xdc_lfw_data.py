#!/usr/bin/python
import argparse
from datetime import datetime
from modules import sentinel2
from modules import clouds
from modules import water
from modules import meteo

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Gets data from satellite')
parser.add_argument("-sd", 
                    "--startdate", 
                    help="The Start Date - format YYYY-MM-DD",
                    required=True,
                    dest='start_date',
                    type=valid_date)
parser.add_argument("-ed", 
                    "--enddate", 
                    help="The Start Date - format YYYY-MM-DD",
                    required=True,
                    dest='end_date',
                    type=valid_date)

parser.add_argument('--region', 
                    dest='region',
                    required=True,
                    choices=['cdp','Sanabria','sanabria'],
                    help='Valid values: cdp, sanabria')

parser.add_argument('--action',
                    dest='action',
                    required=False,
                    choices=['cloud_coverage','cloud_mask','water_surface', 'water_mask', 'meteo'],
                    help='Valid values: cloud_coverage, cloud_mask, water_surface, water_mask')

parser.add_argument('--param',
                    dest='param',
                    required=False,
                    choices=['chl', 'turbidity', 'temp'],
                    help='Valid values: chl, turbidity')

args = parser.parse_args()

#TODO Check end_date > start_date

#TODO Check region to attach coordinates

#Action management
if args.action is not None:
    if args.action == 'cloud_coverage':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        cloud_cov = clouds.cloud_coverage(sat_img)
        print(cloud_cov)
    elif args.action == 'cloud_mask':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        cloud_mask = clouds.cloud_mask(sat_img)
        print(cloud_mask)
    elif args.action == 'water_surface':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        water_sur = water.water_surface(sat_img)
        print(water_sur)
    elif args.action == 'water_mask':
        sat_img = sentinel2.get_sentinel2_raw(args.start_date,args.end_date,args.region)
        water_mask = water.water_mask(sat_img)
        print(water_mask)
    elif args.action == 'meteo':
        meteo = meteo.get_meteo(args.start_date,args.end_date,args.region)
        print(meteo)

print("Fin")
