#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 12:18:03 2018

Prueba para sólo un día

@author: sergio
"""

import datetime
import zipfile
import urllib
import ee
import os
#import gdal
from datetime import timedelta as td

ee.Initialize()


def funct_clorofilas(image):
      return ee.Image(0).expression(
          'float((five/two))',
          {
             'two':image.select('B2'),
             'five':image.select('B5'),
        
          })
def B1(image):
    return ee.Image(0).expression(
            'float((one))',
            {
                    'one':image.select('B1'),
            })
def B3(image):
    return ee.Image(0).expression(
            'float((three))',
            {
                    'three':image.select('B3'),
            })
def B4(image):
    return ee.Image(0).expression(
            'float((four))',
            {
                    'four':image.select('B4'),
            })
def B5(image):
    return ee.Image(0).expression(
            'float((five))',
            {
                    'five':image.select('B5'),
            })
#Para los cirros    
def B9(image):
    return ee.Image(0).expression(
            'float((nine))',
            {
                    'nine':image.select('B9'),
            })
#Para el vapor, banda térmica
def B10(image):
    return ee.Image(0).expression(
            'float((ten))',
            {
                    'ten':image.select('B10'),
            })   
#indice asociado al paper
#Journal of Applied Spectroscopy, Vol. 84, No. 2, May, 2017 (Russian Original Vol. 84, No. 2, March–April, 2017)

def fun_paper(image):
    return ee.Image(0).expression(
            'float((two-four)/three)',
            {
                 'two':image.select('B2'),
                 'four':image.select('B4'),
                 'three':image.select('B3'),
            })
#Creo fecha de salida
fecha_i=datetime.date(year=2013,month=11,day=1)
#Se que el satélite pasa una ve cada 10 dias por tanto si hago intervalos de 10 días me aseguro tener
#una imagen diferente
dias=td(days=21)
#Poligono dentro del cual quiero obtener las imagenes del Sentinel-2

          
geometry = ee.Geometry.Polygon(
       #[[[-4.15, 43.05], [-3.85, 43.05], [-3.85, 42.92], [-4.15, 42.92]]]);
       [[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]);


for i in range (2):
    
    #Imagenes que se encuentren en el poligono anterior y en un rango de fechas,
    #El satelite no recorre toda la superficie terrestre en 1 día.
    #Busco una fecha en la que no haya nubes para poder ver el EC1 y EC2
    s2 = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA').filterBounds(geometry).filterDate(str(fecha_i+dias*i), str(fecha_i+dias*(i+1)));
    list=s2.toList(1)
    id_fecha=list.getInfo()[0]['properties']['DATE_ACQUIRED']
          
    #idnub=list.getInfo()[0]['properties']['CLOUD_COVERAGE_ASSESSMENT']
    #print(id_fecha, idnub)
    print(fecha_i+dias*i)                     
    #Compone todas las imágenes en una sola, por si para ver el lago se necesitaran 2 o mas img.
    imageS2=s2.mosaic();
    
    
    #Se aplica la función a la imagen compuesta anteriormente (hay que descargarlas...)

    cloros=funct_clorofilas(imageS2)
    paper=fun_paper(imageS2)
    b1=B1(imageS2)
    b3=B3(imageS2)
    b4=B4(imageS2)
    b5=B5(imageS2)
    b9=B9(imageS2)
    b10=B10(imageS2)

    path4 =cloros.getDownloadURL({
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })
    path2 =paper.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })    
    pathb1 =b1.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })            
    pathb3 =b3.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })    
    pathb4 =b4.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })    
    pathb5 =b5.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })
    pathb9 =b9.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })
    pathb10 =b10.getDownloadURL({
            
      'scale': 30,
      #'region': '[[-4.11, 43.05], [-3.85, 43.05], [-3.85, 42.94], [-4.11, 42.94]]'
      'region':'[[-2.85, 41.92], [-2.67, 41.92], [-2.67, 41.82], [-2.85, 41.82]]'    
    })  
    #Enlace para descargar la imagen (path)
    
    #almaceno lo que he descargado en una determinada carpeta
    '''
    urllib.request.urlretrieve(path4, '/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/Clorofila/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/Clorofila/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file, '/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/Clorofila/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/Clorofila/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/Clorofila', id_fecha+".tif")
            os.rename(old_file, new_file)
    #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(path2,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/PaperRuso/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/PaperRuso/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/PaperRuso/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/PaperRuso/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/PaperRuso', id_fecha+".tif")
            os.rename(old_file, new_file)
    '''
    #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb1,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1', id_fecha+".tif")
            os.rename(old_file, new_file)
            #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb3,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3', id_fecha+".tif")
            os.rename(old_file, new_file)
            #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb4,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4', id_fecha+".tif")
            os.rename(old_file, new_file)
            #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb5,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5', id_fecha+".tif")
            os.rename(old_file, new_file)
            #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb9,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B9/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B9/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B9/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B9/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B9', id_fecha+".tif")
            os.rename(old_file, new_file)
            #-----------------------------------------------------------------------------------------------------       
    urllib.request.urlretrieve(pathb10,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B10/'+str(id_fecha)+'.zip')
    archive = zipfile.ZipFile('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B10/'+str(id_fecha)+'.zip')
    
    for file in archive.namelist():
        if file.endswith('.tif'):
            archive.extract(file,'/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B10/'+str(id_fecha))
            old_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B10/'+str(id_fecha), file)
            new_file = os.path.join('/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B10', id_fecha+".tif")
            os.rename(old_file, new_file)