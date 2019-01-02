import os

celery_db_user = "user"
celery_db_pass = "pass"

#onedata path and info
onedata_mode = 0
onedata_token = "token"
onedata_url = "https://oneprovider-cnaf.cloud.cnaf.infn.it"
onedata_api = "/api/v3/oneprovider/"
onedata_user = "user"
onedata_space = "LifeWatch"
download_datasets = "datasets"

#local path and info
config_info = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
satelite_info ={'data_path':download_datasets, 'config_path':config_info}

#configure path
if onedata_mode == 1:
    datasets_path = '/onedata/' + onedata_user + '/' + onedata_space + '/' + download_datasets
else:
    datasets_path = satelite_info['data_path']

#Credentials for Sentinel data
sentinel_pass = {'username': "lifewatch",
                 'password': "pass"}

#Credentials for Landsat data
landsat_pass = {'username': "lifewatch",
                'password': "pass"}

#info regions
regions = {"CdP":{"id":210788, "coordinates": {"W": -2.830 , "S": 41.820, "E": -2.690, "N": 41.910}},
           "Francia": {"id":234185, "coordinates":{"W": 1.209, "S": 47.807, "E": 2.314, "N": 48.598}},
	       "Niger": {"id": 874916, "coordinates":{"W": 11.162, "S": 18.380, "E": 12.338, "N":19.554}},
           "Brasil": {"id": 187392, "coordinates":{"W": -37.764, "S": -10.602, "E": -32.047, "N": -7.384}},
	       "Oceano Pacifico": {"id": 187392, "coordinates":{"W": -155.204, "S": -0.656, "E": -155.195, "N": -0.649}},
	       "Siberia": {"id": 187392, "coordinates":{"W": 106.573, "S": 54.158, "E": 106.676, "N": 54.219}},
	       "India": {"id": 187392, "coordinates":{"W": 75.889, "S": 22.786, "E": 78.026, "N": 24.965}},
	       "Canada": {"id": 187392, "coordinates":{"W": -122.106, "S": 51.229, "E": -122.049, "N": 51.261}},
	       "USA": {"id": 187392, "coordinates":{"W": -86.136, "S": 34.960, "E": -86.084, "N": 35.001}},
	       "Polonia": {"id": 187392, "coordinates":{"W": 18.345, "S": 50.958, "E": 18.463, "N": 51.027}},
	       "Tunez": {"id": 187392, "coordinates":{"W": 9.777, "S": 36.260, "E": 10.921, "N": 36.924}},
	       "Antartida": {"id": 187392, "coordinates":{"W": 83.571, "S": -74.779, "E": 83.578, "N": -74.777}},
	       "Australia": {"id": 187392, "coordinates":{"W": 139.876, "S": -21.880, "E": 139.880, "N": -21.875}},
	       "China": {"id": 187392, "coordinates":{"W": 107.623, "S": 28.631, "E": 107.626, "N": 28.634}},
	       "Finlandia": {"id": 187392, "coordinates":{"W": 19.769, "S": 60.967, "E": 23.465, "N": 62.250}},
	       "South Africa": {"id": 187392, "coordinates":{"W": 21.796, "S": -29.419, "E": 21.948, "N": -29.284}},
	       "Japon": {"id": 187392, "coordinates":{"W": 137.460, "S": 35.587, "E": 141.360, "N": 36.813}},
	       "Alemania": {"id": 187392, "coordinates":{"W": 9.938, "S": 50.467, "E": 9.978, "N": 50.486}}}

#actions
keywords = ['cloud_mask', 'cloud_coverage', 'water_mask', 'water_surface']
