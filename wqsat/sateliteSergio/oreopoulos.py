#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:40:59 2018

@author: sergio
"""

from scipy import misc
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#Algoritmo clasificacion

def oreopoulos(b1,b3,b4,b5):
    B1=misc.imread(b1)
    B3=misc.imread(b3)
    B4=misc.imread(b4)
    B5=misc.imread(b5)
    m,n = B1.shape
    print(m*n)
    sol=np.zeros(shape=(m,n))
    for i in range (m):
        for j in range (n):
            if(((B1[i,j]<B3[i,j]) & (B3[i,j]<B4[i,j]) & (B4[i,j]<B5[i,j]*1.07) & (B5[i,j]<0.65)) | 
            ((B1[i,j]*0.8<B3[i,j]) & (B3[i,j]<B4[i,j]*0.8) & (B4[i,j]<B5[i,j]) & (B3[i,j]<0.22))):
                #Non Vegetated Lands
                sol[i,j]=0
            elif(((B3[i,j]>0.24) & (B5[i,j]<0.16) & (B3[i,j]>B4[i,j])) |
            ((0.24<B3[i,j]<0.18) & (B5[i,j]<B3[i,j]-0.08) & (B3[i,j]>B4[i,j]))):
                #Snow/Ice
                sol[i,j]=63
            elif(((B3[i,j]>B4[i,j]) & (B3[i,j]>B5[i,j]*0.67) & (B1[i,j]<0.3) & (B3[i,j]<0.20)) |
            ((B3[i,j]>B4[i,j]*0.8) & (B3[i,j]>B5[i,j]*0.67) & (B3[i,j]<0.06))):
                #Water Bodies
                sol[i,j]=127
            elif(((B1[i,j]>0.20) | (B3[i,j]>0.18)) & (B5[i,j]>0.16) & (max(B1[i,j],B3[i,j])>B5[i,j]*0.67)):
                #Clouds
                sol[i,j]=191
            else:
                #Vegetated Lands
                sol[i,j]=255
    return(sol)

lugar='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B1'
lugar_4='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B4'
lugar_3='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B3'
lugar_5='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8/B5'
files = os.listdir(lugar)
files_4 = os.listdir(lugar_4)
files_3 = os.listdir(lugar_3)
files_5 = os.listdir(lugar_5)
b1s=[]
b3s=[]
b4s=[]
b5s=[]
for file in files:
        if file.endswith('.tif'):
            path_file = os.path.join(lugar, file)
            
            b1s.append(path_file)
for file in files_3:
        if file.endswith('.tif'):
            path_file = os.path.join(lugar_3, file)
            
            b3s.append(path_file)
for file in files_4:
        if file.endswith('.tif'):
            path_file = os.path.join(lugar_4, file)
            
            b4s.append(path_file)
for file in files_5:
        if file.endswith('.tif'):
            path_file = os.path.join(lugar_5, file)
            
            b5s.append(path_file)
imagenes=[]
for i in range(2):
        imagenes.append(oreopoulos(os.path.join(lugar,b1s[i]),os.path.join(lugar_3,b3s[i])
        ,os.path.join(lugar_4,b4s[i]),os.path.join(lugar_5,b5s[i])))
                
"""
nubes=[]
cloros=[]
fechas=[]
papers=[]

for file in files:
        if file.endswith('.tif'):
            path_file = os.path.join(lugar, file)
            porcentaje=(cloud_image_tiff(path_file)) 
            nubes.append(porcentaje)
for file2 in files_2:
        if file2.endswith('.tif'):
            path_file2 = os.path.join(lugar_2,file2)
            clor=(mean_cloros_tiff(path_file2))
            cloros.append(clor)
for file in files:
        if file.endswith('.tif'):
            fechas.append(file[:-4])
for file3 in files_3:
    if file3.endswith('.tif'):
        path_file3=os.path.join(lugar_3,file3)
        paper=mean_cloros_tiff(path_file3)
        papers.append(paper)
"""

