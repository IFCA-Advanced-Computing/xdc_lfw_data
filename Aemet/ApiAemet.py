#Importamos todas las librerias que vamos a utilizar
import http.client
import ssl
import json
import csv
import xml.etree.cElementTree as ET
#import urllib

#Para que no tengamos problemas con los certificados.
ssl._create_default_https_context = ssl._create_unverified_context

#Definimos la key para conectarse a la api de aemet
key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2aWxsYXJyakB1bmljYW4uZXMiLCJqdGkiOiJkZDc5ZjVmNy1hODQwLTRiYWQtYmMzZi1jNjI3Y2ZkYmUxNmYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTUyMDg0NzgyOSwidXNlcklkIjoiZGQ3OWY1ZjctYTg0MC00YmFkLWJjM2YtYzYyN2NmZGJlMTZmIiwicm9sZSI6IiJ9.LMl_cKCtYi3RPwLwO7fJYZMes-bdMVR91lRFZbUSv84'

#Creamos la conexión con la web de opendata para que este disponible en todas las funciones.
conn = http.client.HTTPSConnection("opendata.aemet.es")
#Definimos la cabecera de la web
headers = {'cache-control': "no-cache" }


"""Lo primero que debemos hacer es obtener todas las estaciones para conocer su identificador 
y asi buscar los resgistros historicos para la zona que queramos."""
""" Para buscar le pasaremos la provincia donde queremos que se encuentren las estaciones"""
def buscarEstaciones(key,provincia):
    #Obtenemos todas las características de todas las estaciones climatológicas
    conn.request("GET", "/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key="+key, headers=headers)
    #Realizamos la conexión  y obtenemos el objeto que almacena la direción donde se encuentran las estaciones
    res = conn.getresponse()
    #Leemos los datos y decodificamos
    datosTodasEstaciones = res.read().decode('latin')
    #Transformamos los datos a formato json
    datosTodasEstaciones = json.loads(datosTodasEstaciones)
    #Una vez tenemos la ruta, obtenemos los datos de las estaciones
    conn.request("GET", datosTodasEstaciones['datos'], headers=headers)
    #Obtenemos la ruta
    res= conn.getresponse()
    #Transformamos los datos a formato json
    datosEstaciones = res.read().decode('latin','ignore')
    datosEstaciones= json.loads(datosEstaciones)
    
    #Buscamos todas las estaciones de las provincia deseada
    estacionesEncontradas=[]
    for estacion in datosEstaciones:
        if(estacion['provincia']==provincia.upper()):
            estacionesEncontradas.append(estacion)
    #Devolvemos todas las estaciones encontradas
    return estacionesEncontradas


#Vamos a crear un método que nos devuelva los datos de una estación
#La API solo permite hacer consultas de 31 días máximo
def datosEstacion(key,fechaIni,fechaFin,estaciones):
    #Lista que almacena la estación y los valores.
    salidaInformacion=[]
    if (type(estaciones))==dict:
        print ("pepe")
    with open('pruebaEstaciones.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["Fecha","Tmed","Indicativo"])
        for estacion in estaciones:
            #print(estacion)
            #salidaInformacion[0][0]=2
            conn.request("GET", "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+fechaIni+"/fechafin/"+fechaFin+"/estacion/"+estacion['indicativo']+"/?api_key="+key, headers=headers)
            res = conn.getresponse()
            dataSantander = res.read().decode('utf-8')
            dataSantander = json.loads(dataSantander)
            #print("Primera parte")
            #print(dataSantander)
            #print("Segunda parte")
            conn.request("GET", dataSantander['datos'], headers=headers)
            res= conn.getresponse()
            datosSantander = res.read().decode('utf-8','ignore')
            datosSantander= json.loads(datosSantander)
            #Añadimos los datos a la lista
            salidaInformacion.append([estacion,datosSantander])
            for resultados in datosSantander:
                #print(resultados['fecha'],":",resultados['tmed'],"C")
                spamwriter.writerow([resultados['fecha'], resultados['tmed'],resultados['indicativo']])
            
            #print(datosSantander)
            #print ("Otra")
    return salidaInformacion
    
#Método usado para guardar la información en un csv
    def guardarInformacion (datos):
        with open('prueba.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(["Fecha","Tmed"])
            for resultados in datos:
                #print(resultados['fecha'],":",resultados['tmed'],"C")
                spamwriter.writerow([resultados['fecha'], resultados['tmed']])

#Método usado para crear los metadatos del csv
def crearMetadatos(estaciones):
    #Creamos un archivo de metadatos asociado al archivo anterior
    eml = ET.Element("eml:eml",system="knb",xmlns="eml://ecoinformatics.org/eml-2.1.1")
    acceso = ET.SubElement(eml, "access", authSystem="knb", order="allowFirst")
    permiso=ET.SubElement(acceso,"allow")
    ET.SubElement(permiso,"principal").text="público"
    ET.SubElement(permiso,"permission").text="lectura"
    #Creamos otro hijo de eml
    dataset=ET.SubElement(eml,"dataset")
    ET.SubElement(dataset,"title").text="Datos de temperatura media en enero"
    coverage=ET.SubElement(dataset,"coverage")
    for estacion in estaciones:
        coverageG=ET.SubElement(coverage,"geographicCoverage")
        ET.SubElement(coverageG,"geographicDescription").text="Santander"
        ET.SubElement(coverageG,"gRingLatitude").text=estacion['latitud']
        ET.SubElement(coverageG,"gRingLongitude").text=estacion['longitud']
        ET.SubElement(coverageG,"altitude").text=estacion['altitud']
    #coverageT=ET.SubElement(coverage,"temporalCoverage")
    #ET.SubElement(coverageT,"FechaComienzo").text=datosSantander[0]['fecha']
    #ET.SubElement(coverageT,"FechaComienzo").text=datosSantander[30]['fecha']
    tablaDatos=ET.SubElement(dataset,"dataTable")
    ET.SubElement(tablaDatos,"NombreArchivo").text="prueba1.csv"
    atributoLista=ET.SubElement(tablaDatos,"attributeList")
    atributoFecha=ET.SubElement(atributoLista,"attribute",id="Fecha")
    ET.SubElement(atributoFecha,"name").text="Fecha"
    ET.SubElement(atributoFecha,"formatString").text="YYYY-MM-DD"
    atributoTemp=ET.SubElement(atributoLista,"attribute",id="Temperatura")
    ET.SubElement(atributoTemp,"name").text="Temperatura"
    ET.SubElement(atributoTemp,"Unidadades").text="ºC"
    tree = ET.ElementTree(eml)

    #Escribimos los datos en un archivo
    tree.write("filename3.xml",encoding='UTF-8', xml_declaration=True,short_empty_elements=True)
    #print(tree)


print("hhh")


prueba1=buscarEstaciones(key,'Cantabria')


print(prueba1)
#print(prueba1)
#data=encontrarTodasEstaciones(key)

fechaI="2018-01-01T00%3A00%3A00UTC"
fechaF="2018-01-31T00%3A00%3A00UTC"


tt=datosEstacion(key,"2018-01-30T00%3A00%3A00UTC","2018-01-31T00%3A00%3A00UTC",prueba1[0:3])


crearMetadatos(prueba1[0:3])


#crearMetadatos(prueba1)


#Ahora que tenemos el indicativo vamos a consultar para esa estacion
#GET /api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}




#Vemos los resultados.
#for resultados in datosSantander:
#    print(resultados['fecha'],":",resultados['tmed'],"C")
 
#with open('prueba.csv', 'w', newline='') as csvfile:
#    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#    spamwriter.writerow(["Fecha","Tmed"])
#    
#    for resultados in datosSantander:
#        #print(resultados['fecha'],":",resultados['tmed'],"C")
#        spamwriter.writerow([resultados['fecha'], resultados['tmed']])




#Preguntar etiqueta de altitude