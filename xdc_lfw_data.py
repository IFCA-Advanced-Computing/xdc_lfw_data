import argparse
from datetime import datetime

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
