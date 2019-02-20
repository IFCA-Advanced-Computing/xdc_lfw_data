#!/usr/bin/python3
import argparse

from wq_modules import config
from wq_modules import clouds
from wq_modules import water
from wq_modules import utils
from wq_modules import sentinel
from wq_modules import landsat

parser = argparse.ArgumentParser(description='Gets data from satellite')

parser.add_argument("-sd",
                    "--startdate",
                    help="The Start Date - format DD-MM-YYYY",
                    required=True,
                    dest='start_date')

parser.add_argument("-ed",
                    "--enddate",
                    help="The Start Date - format DD-MM-YYYY",
                    required=True,
                    dest='end_date')

parser.add_argument('--region',
                    dest='region',
                    required=True,
                    choices=['CdP','Sanabria','Cogotas'],
                    help='Valid values: CdP, Sanabria, Cogotas')

parser.add_argument('--action',
                    dest='action',
                    required=False,
                    choices=['cloud_coverage','cloud_mask','water_surface', 'water_mask', 'raw'],
                    help='Valid values: cloud_coverage, cloud_mask, water_surface, water_mask, raw')

parser.add_argument('--param',
                    dest='param',
                    required=False,
                    choices=['chl', 'turbidity'],
                    help='Valid values: chl, turbidity')

args = parser.parse_args()

#Check the format date and if end_date > start_date
sd, ed = utils.valid_date(args.start_date, args.end_date)

#chek the region to attach coordinates
utils.valid_region(args.region)

#check if the action exist in the Keywords list of config file
utils.valid_action(args.action)

#Configure the tree of the temporal datasets path. Create the folder and the downloaded_files file
onedata_mode = config.onedata_mode
utils.path_configurations(onedata_mode)

#Action management
if args.action is not None:

    #download sentinel files
    s = sentinel.Sentinel(sd, ed, args.region, args.action)
    s.download()
    sentinel_files = s.__dict__['output']

    #download landsat files
    l = landsat.Landsat(sd, ed, args.region, args.action)
    l.download()
    landsat_files = l.__dict__['output']
    
    if onedata_mode == 1:
        utils.to_onedata(sentinel_files, landsat_files, args.region)
        utils.clean_temporal_path()

    if args.action == 'water_mask' or args.action == 'water_surface':
        
        water.main_water(sentinel_files, landsat_files, args.region, args.action)

    elif args.action == 'cloud_mask' or args.action == 'cloud_coverage':

        clouds.main_cloud(sentinel_files, landsat_files, args.region, args.action)
