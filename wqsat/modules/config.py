import os
#Meteo module params

METEO_API_TOKEN='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2aWxsYXJyakB1bmljYW4uZXMiLCJqdGkiOiJkZDc5ZjVmNy1hODQwLTRiYWQtYmMzZi1jNjI3Y2ZkYmUxNmYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTUyMDg0NzgyOSwidXNlcklkIjoiZGQ3OWY1ZjctYTg0MC00YmFkLWJjM2YtYzYyN2NmZGJlMTZmIiwicm9sZSI6IiJ9.LMl_cKCtYi3RPwLwO7fJYZMes-bdMVR91lRFZbUSv84'
METEO_API_URL='opendata.aemet.es'

#Storage parameters
onedata_mode = 1
onedata_token = 'MDAxNWxvY2F00aW9uIG9uZXpvbmUKMDAzMGlkZW500aWZpZXIgMDRmMGQxODRmMTBmODAxN2ZkNTNkNGJlYWIyNjc3NTkKMDAxYWNpZCB00aW1lIDwgMTU2MzM00NDg00MQowMDJmc2lnbmF00dXJlIGy97Y8H4rGIxCMYsJSHQg1v6BpLGAwnDL01EE6AFAs1BCg'
onedata_url = 'https://oneprovider-cnaf.cloud.cnaf.infn.it'
onedata_api = '/api/v3/oneprovider/'
onedata_space = 'LifeWatch'
onedata_user = "user"
download_datasets = 'datasets'
config_info = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Satelite module params
satelite_info ={'data_path':download_datasets, 'config_path':config_info}
regions ={'regions': {
"CdP": [[-2.830, 41.910], [-2.690, 41.910], [-2.690, 41.820], [-2.830, 41.820], [-2.830, 41.910]],
"Sanabria": [[-6.741, 42.133], [-6.742, 42.107], [-6.694, 42.107], [-6.694, 42.134], [-6.741, 42.133]],
"Cogotas": [[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]
}}
