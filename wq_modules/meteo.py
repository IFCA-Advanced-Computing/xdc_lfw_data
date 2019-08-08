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

class Meteo:

    def __init__(self, inidate, enddate, region):

        #data for download files
        self.inidate = inidate
        self.enddate = enddate
        self.region = region
        self.coord = config.regions[region]["coordinates"]

        #Get Latitude, Longitude
        self.lon = self.coord['W']
        self.lat = self.coord['N']


        self.station = ''
        self.general_name = ''
        self.params = ["ID","Date","Temp"]

        #metadata of the data
        self.metadata = {'region': region, # place / reservoir / name of the list
                         'id': config.regions[region]["id"],
                         'coord': config.regions[region]["coordinates"]
                         }

        #work path
        self.path = config.datasets_path

        #meteo credentials
        self.credentials = config.METEO_API_TOKEN

        #AEMET APIs
        self.api_url = config.METEO_API_URL


    """Lo primero que debemos hacer es obtener todas las estaciones para conocer su identificador 
    y asi buscar los resgistros historicos para la zona que queramos."""
    """ Para buscar le pasaremos la provincia donde queremos que se encuentren las estaciones"""
    def find_station(self):
        conn = http.client.HTTPSConnection(self.api_url)
        headers = {'cache-control': "no-cache" }
        conn.request("GET", "/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key="+self.credentials, headers=headers)
        res = conn.getresponse()
        datosTodasEstaciones = res.read().decode('latin')
        datosTodasEstaciones = json.loads(datosTodasEstaciones)
        conn.request("GET", datosTodasEstaciones['datos'], headers=headers)
        res= conn.getresponse()
        datosEstaciones = res.read().decode('latin','ignore')
        datosEstaciones= json.loads(datosEstaciones)
        conn.close()
        
        print(self.lon)

        #Find closest station
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
            if (abs(self.lon-lon_temp) + abs(self.lat-lat_temp)) < min_station:
                self.station = search['indicativo']
                min_station = abs(self.lon-lon_temp) + abs(self.lat-lat_temp)
                print('Estacion %s - %s || %s, %s' % (search['indicativo'],search['nombre'],lat_temp,lon_temp))
        return self.station

    def datosEstacion(self):
        headers = {'cache-control': "no-cache" }
        conn = http.client.HTTPSConnection(self.api_url)
        salidaInformacion=[]
        with open(self.general_name+'.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(self.params)
            delta = self.enddate-self.inidate
            if (delta.days <31):
                req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+self.inidate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+self.enddate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+self.station+"/?api_key="+self.credentials
                conn.request("GET",req, headers=headers)
                res = conn.getresponse()
                dataEstacion = res.read().decode('utf-8')
                dataEstacion = json.loads(dataEstacion)
                conn.request("GET", dataEstacion['datos'], headers=headers)
                res= conn.getresponse()
                datosEstacion = res.read().decode('utf-8','ignore')
                datosEstacion= json.loads(datosEstacion)
                salidaInformacion.append([self.station,datosEstacion])
                for resultados in datosEstacion:
                    #print(resultados['fecha'],":",resultados['tmed'],"C")
                    try:
                        wrt = []
                        if 'velmedia' in resultados:
                            resultados['velmedia'] = resultados['velmedia'].replace(',', '.')
                        for e in self.translate_params():
                            wrt.append(resultados[e])
                        spamwriter.writerow(wrt)
                    except Exception as e:
                        print(e)
                conn.close()
            else:
                temp_end_date = self.inidate + datetime.timedelta(days=30)
                while(temp_end_date < self.enddate):
                    req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+self.inidate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+temp_end_date.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+self.station+"/?api_key="+self.credentials
                    conn.request("GET",req, headers=headers)
                    res = conn.getresponse()
                    dataEstacion = res.read().decode('utf-8')
                    dataEstacion = json.loads(dataEstacion)
                    conn.request("GET", dataEstacion['datos'], headers=headers)
                    res= conn.getresponse()
                    datosEstacion = res.read().decode('utf-8','ignore')
                    datosEstacion= json.loads(datosEstacion)
                    salidaInformacion.append([self.station,datosEstacion])
                    for resultados in datosEstacion:
                        #print(resultados['fecha'],":",resultados['tmed'],"C")
                        try:
                            wrt = []
                            if 'velmedia' in resultados:
                                resultados['velmedia'] = resultados['velmedia'].replace(',', '.')
                            for e in self.translate_params():
                                wrt.append(resultados[e])
                            spamwriter.writerow(wrt)
                        except Exception as e:
                            print(e)
                    conn.close()
                    self.inidate = temp_end_date
                    temp_end_date = self.inidate + datetime.timedelta(days=30)
            
                req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+self.inidate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/fechafin/"+self.enddate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC"+"/estacion/"+self.station+"/?api_key="+self.credentials
                print(req)
                conn.request("GET",req, headers=headers)
                res = conn.getresponse()
                dataEstacion = res.read().decode('utf-8')
                dataEstacion = json.loads(dataEstacion)
                conn.request("GET", dataEstacion['datos'], headers=headers)
                res= conn.getresponse()
                datosEstacion = res.read().decode('utf-8','ignore')
                datosEstacion= json.loads(datosEstacion)
                salidaInformacion.append([self.station,datosEstacion])
                for resultados in datosEstacion:
                    #print(resultados['fecha'],":",resultados['tmed'],"C")
                    try:
                        wrt = []
                        if 'velmedia' in resultados:
                            resultados['velmedia'] = resultados['velmedia'].replace(',', '.')
                        for e in self.translate_params():
                            wrt.append(resultados[e])
                        spamwriter.writerow(wrt)
                    except Exception as e:
                        print(e)
                conn.close()
        csvfile.close()
        return salidaInformacion

    def get_meteo(self):
        prefix = ''
        if 'Temp' in self.params:
            prefix = 'temp_'
        elif 'speed' in self.params:
            prefix = 'wind_'
        self.general_name = self.path + '/' + self.region + '/' + prefix + self.inidate.strftime('%Y-%m-%d')+"_"+self.enddate.strftime('%Y-%m-%d')
        title = prefix + self.inidate.strftime('%Y-%m-%d')+"_"+self.enddate.strftime('%Y-%m-%d')+".csv"
        beginDate = self.inidate.strftime('%Y-%m-%d')
        endDate = self.enddate.strftime('%Y-%m-%d')
        self.station = self.find_station() #TODO add lat/lon
        print("Selected station: "+self.station)
        tt=self.datosEstacion()
        if (config.onedata_mode == 1):
            metadata_gen.metadata_gen(title,beginDate,endDate,self.region,str(self.lat),str(self.lon),self.params)
        return {"output": self.general_name + ".csv"}

    """Method for trasnlating from original parameter names to AEMET param names"""
    def translate_params(self):
        aemet_params = []
        for e in self.params:
            if e == "ID":
                aemet_params.append('indicativo')
            if e == "Date":
                aemet_params.append('fecha')
            if e == "date":
                aemet_params.append('fecha')
            if e == "Temp":
                aemet_params.append('tmed')
            if e == "speed":
                aemet_params.append('velmedia')
            if e == "dir":
                aemet_params.append('dir')
        return aemet_params
