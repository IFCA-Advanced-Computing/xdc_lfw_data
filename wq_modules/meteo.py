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

import http.client
import ssl
import json
import csv
import datetime
import xml.etree.cElementTree as ET
from wq_modules import metadata_gen
from wq_modules import config

"""Lo primero que debemos hacer es obtener todas las estaciones para conocer su identificador 
y asi buscar los resgistros historicos para la zona que queramos."""
""" Para buscar le pasaremos la provincia donde queremos que se encuentren las estaciones"""
def find_station(key,api,lat,lon):
    conn = http.client.HTTPSConnection(api)
    headers = {'cache-control': "no-cache" }
    conn.request("GET", "/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key="+key, headers=headers)
    res = conn.getresponse()
    datosTodasEstaciones = res.read().decode('latin')
    datosTodasEstaciones = json.loads(datosTodasEstaciones)
    conn.request("GET", datosTodasEstaciones['datos'], headers=headers)
    res= conn.getresponse()
    datosEstaciones = res.read().decode('latin','ignore')
    datosEstaciones= json.loads(datosEstaciones)
    conn.close()

    #Find closest station
    station = ''
    min_station = 9999
    for search in datosEstaciones:
        if search['latitud'][-1] == 'N':
            lat_temp = float(search['latitud'][0:-1])*0.0001
        else:
            lat_temp = float(search['latitud'][0:-1])*-0.0001
        if search['longitud'][-1] == "E":
            lon_temp = float(search['longitud'][0:-1])*0.0001
        else:
            lon_temp = float(search['longitud'][0:-1])*-0.0001
        if (abs(lon-lon_temp) + abs(lat-lat_temp)) < min_station:
            station = search['indicativo']
            min_station = abs(lon-lon_temp) + abs(lat-lat_temp)
            print('Estacion %s - %s || %s, %s' % (search['indicativo'],search['nombre'],lat_temp,lon_temp))
    return station

def datosEstacion(key,api,start_date,end_date,station,general_name,params):
    headers = {'cache-control': "no-cache" }
    conn = http.client.HTTPSConnection(api)
    salidaInformacion=[]
    with open(general_name+'.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(params)
        delta = end_date-start_date
        if (delta.days <31):
            req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+start_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+end_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+station+"/?api_key="+key
            print(req)
            conn.request("GET",req, headers=headers)
            res = conn.getresponse()
            dataEstacion = res.read().decode('utf-8')
            dataEstacion = json.loads(dataEstacion)
            conn.request("GET", dataEstacion['datos'], headers=headers)
            res= conn.getresponse()
            datosEstacion = res.read().decode('utf-8','ignore')
            datosEstacion= json.loads(datosEstacion)
            salidaInformacion.append([station,datosEstacion])
            for resultados in datosEstacion:
                #print(resultados['fecha'],":",resultados['tmed'],"C")
                try:
                    spamwriter.writerow([resultados['indicativo'],resultados['fecha'], resultados['tmed']])
                except:
                    print('punch')
            conn.close()
        else:
            temp_end_date = start_date + datetime.timedelta(days=30)
            while(temp_end_date < end_date):
                req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+start_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+temp_end_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+station+"/?api_key="+key
                print(req)
                conn.request("GET",req, headers=headers)
                res = conn.getresponse()
                dataEstacion = res.read().decode('utf-8')
                dataEstacion = json.loads(dataEstacion)
                conn.request("GET", dataEstacion['datos'], headers=headers)
                res= conn.getresponse()
                datosEstacion = res.read().decode('utf-8','ignore')
                datosEstacion= json.loads(datosEstacion)
                salidaInformacion.append([station,datosEstacion])
                for resultados in datosEstacion:
                    #print(resultados['fecha'],":",resultados['tmed'],"C")
                    try:
                        spamwriter.writerow([resultados['indicativo'],resultados['fecha'], resultados['tmed']])
                    except:
                        print('punch')
                conn.close()
                start_date = temp_end_date
                temp_end_date = start_date + datetime.timedelta(days=30)
            
            req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+start_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+end_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+station+"/?api_key="+key
            print(req)
            conn.request("GET",req, headers=headers)
            res = conn.getresponse()
            dataEstacion = res.read().decode('utf-8')
            dataEstacion = json.loads(dataEstacion)
            conn.request("GET", dataEstacion['datos'], headers=headers)
            res= conn.getresponse()
            datosEstacion = res.read().decode('utf-8','ignore')
            datosEstacion= json.loads(datosEstacion)
            salidaInformacion.append([station,datosEstacion])
            for resultados in datosEstacion:
                #print(resultados['fecha'],":",resultados['tmed'],"C")
                try:
                    spamwriter.writerow([resultados['indicativo'],resultados['fecha'], resultados['tmed']])
                except:
                    print('punch')
            conn.close()
    csvfile.close()
    return salidaInformacion

def get_meteo(start_date, end_date, region):
    #onedata mode
    if (config.onedata_mode == 1):
        datasets_path = '/onedata/' + config.onedata_user + '/' + config.onedata_space + '/' + config.download_datasets
    else:
        datasets_path = '.' + config.download_datasets
   
    general_name = datasets_path + '/' + region + '/' + "meteo_"+start_date.strftime('%Y-%m-%d')+"_"+end_date.strftime('%Y-%m-%d')
    METEO_API_TOKEN=config.METEO_API_TOKEN
    METEO_API_URL=config.METEO_API_URL

    #Get Latitude, Longitude
    coords = config.regions['regions'][region]
    lon = 0
    for l in coords:
        lon = lon + l[0]
    lon = lon/len(coords)
    lat = 0
    for l in coords:
        lat = lat + l[1]
    lat = lat/len(coords)
    print("Lat: %s Lon: %s" % (lat,lon))
    station = find_station(METEO_API_TOKEN,METEO_API_URL,lat,lon) #TODO add lat/lon
    print(station)
    params = ["ID","Date","Temp"] #TODO add wind, prec
    tt=datosEstacion(METEO_API_TOKEN,METEO_API_URL,start_date,end_date,station,general_name,params)
    metadata_gen.metadata_gen(general_name,start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d'),region,str(lat),str(lon),params)
    return {"output": general_name}
