import config
import http.client
import ssl
import json
import csv
import xml.etree.cElementTree as ET
from modules import metadata_gen

"""Lo primero que debemos hacer es obtener todas las estaciones para conocer su identificador 
y asi buscar los resgistros historicos para la zona que queramos."""
""" Para buscar le pasaremos la provincia donde queremos que se encuentren las estaciones"""
def buscarEstaciones(key,api,lat,lon):
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

    #Buscamos la estacion mas cercana
    #TODO
    provincia='Cantabria' #TODO delete
    estacionesEncontradas=[]
    for estacion in datosEstaciones:
        if(estacion['provincia']==provincia.upper()):
            estacionesEncontradas.append(estacion)
    #Devolvemos todas las estaciones encontradas
    conn.close()
    return estacionesEncontradas

def datosEstacion(key,api,fechaIni,fechaFin,estacion,general_name):
    headers = {'cache-control': "no-cache" }
    conn = http.client.HTTPSConnection(api)
    salidaInformacion=[]
    with open(general_name+'.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["Date","Tmed","Id"])
        req = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+fechaIni+"/fechafin/"+fechaFin+"/estacion/"+estacion+"/?api_key="+key
        print(req)
        conn.request("GET",req, headers=headers)
        res = conn.getresponse()
        dataEstacion = res.read().decode('utf-8')
        dataEstacion = json.loads(dataEstacion)
        conn.request("GET", dataEstacion['datos'], headers=headers)
        res= conn.getresponse()
        datosEstacion = res.read().decode('utf-8','ignore')
        datosEstacion= json.loads(datosEstacion)
        salidaInformacion.append([estacion,datosEstacion])
        for resultados in datosEstacion:
            #print(resultados['fecha'],":",resultados['tmed'],"C")
            spamwriter.writerow([resultados['fecha'], resultados['tmed'],resultados['indicativo']])
    conn.close()
    return salidaInformacion

def get_meteo(startDate, endDate, region):
    general_name = region+"_"+startDate.strftime('%Y-%m-%d')+"_"+endDate.strftime('%Y-%m-%d')
    METEO_API_TOKEN='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2aWxsYXJyakB1bmljYW4uZXMiLCJqdGkiOiJkZDc5ZjVmNy1hODQwLTRiYWQtYmMzZi1jNjI3Y2ZkYmUxNmYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTUyMDg0NzgyOSwidXNlcklkIjoiZGQ3OWY1ZjctYTg0MC00YmFkLWJjM2YtYzYyN2NmZGJlMTZmIiwicm9sZSI6IiJ9.LMl_cKCtYi3RPwLwO7fJYZMes-bdMVR91lRFZbUSv84'
    METEO_API_URL='opendata.aemet.es'
    stations = buscarEstaciones(METEO_API_TOKEN,METEO_API_URL,region,region) #TODO add lat/lon
    estacion=stations[0]
    print(estacion)
    tt=datosEstacion(METEO_API_TOKEN,METEO_API_URL,startDate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC",endDate.strftime('%Y-%m-%d')+"T00%3A00%3A00UTC",estacion['indicativo'],general_name)
    metadata_gen.metadata_gen(general_name,startDate.strftime('%Y-%m-%d'),endDate.strftime('%Y-%m-%d'),region,"-3.43","41.33",general_name)
    return "done"
