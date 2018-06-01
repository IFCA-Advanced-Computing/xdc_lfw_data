# -*- coding: utf-8 -*-
"""
Ver qué imágenes tienen menos de un 15% de nubes, y de ellas sacar la clorofila

@author: SSL
"""
from sklearn import datasets, linear_model
from scipy import misc
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt


#Función de porcentaje nubosidad
def oreopoulos(b1,b3,b4,b5):
    B1=misc.imread(b1)
    B3=misc.imread(b3)
    B4=misc.imread(b4)
    B5=misc.imread(b5)
    m,n = B1.shape
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
        

def cloud_image_tiff(b1,b3,b4,b5,sombra):

    sol=oreopoulos(b1,b3,b4,b5)
    m,n = misc.imread(b1).shape
    nubes=0
    for i in range (m):
        for j in range (n):
            if sol[i,j]==127:
                nubes=nubes+1
    porcentaje=nubes/(m*n)
    if porcentaje<sombra:
        return False
        print(t)
    else :
        return True
        print(f)
    #mask_cloud= (B4>2500)
    #mask_cloud = mask_cloud.reshape(m,n)
    #plt.title("Mask Cloud")
    #plt.imshow(mask_cloud)
    #plt.colorbar
    

def mean_cloros_tiff(path):
    clor=misc.imread(path)
    m,n=clor.shape
    mean_clor=sum(sum(clor))/(m*n)
    #mean_clor=clor[1,3]
    return(mean_clor)
'''
def getQABits(image, start, end, mascara):
    # Compute the bits we need to extract.
    pattern = 0
    for i in range(start,end+1):
        pattern += 2**i
    # Return a single band image of the extracted QA bits, giving the     band a new name.
    return image.select([0], [mascara]).bitwiseAnd(pattern).rightShift(start)
#A function to mask out cloudy pixels.
def maskQuality(image):
    # Select the QA band.
    QA = image.select('QA')
    # Get the internal_cloud_algorithm_flag bit.
    sombra = getQABits(QA,3,3,'cloud_shadow')
    nubes = getQABits(QA,5,5,'cloud')
    #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
    cirrus_detected = getQABits(QA,9,9,'cirrus_detected')
    #var cirrus_detected2 = getQABits(QA,8,8,  'cirrus_detected2')
    #Return an image masking out cloudy areas.
    return image.updateMask(sombra.eq(0)).updateMask(nubes.eq(0).updateMask(cirrus_detected.eq(0)))
'''

lugar_1='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8Cog/Clorofila'
lugar_2='/media/sergio/Datos/Escritorio_Sergio/Estudio embalses/Landsat8Cog/PaperRuso'

files_1 = os.listdir(lugar_1)
files_2 = os.listdir(lugar_2)

cloros=[]
fechas=[]
papers=[]

for file1 in files_1:
        if file1.endswith('.tif'):
            path_file1 = os.path.join(lugar_2,file1)
            clor=(mean_cloros_tiff(path_file1))
            cloros.append(clor)
for file in files_1:
        if file.endswith('.tif'):
            fechas.append(file[:-4])
for file2 in files_2:
    if file2.endswith('.tif'):
        path_file2=os.path.join(lugar_2,file2)
        paper=mean_cloros_tiff(path_file2)
        papers.append(paper)
            
#Junto todo en un DataFrame
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
for i in range(len(b1s)):
        imagenes.append(cloud_image_tiff(os.path.join(lugar,b1s[i]),os.path.join(lugar_3,b3s[i])
        ,os.path.join(lugar_4,b4s[i]),os.path.join(lugar_5,b5s[i]),0.1))

datos=pd.DataFrame({'fechas':fechas,'nubes':imagenes,'cloros':cloros, 'papers':papers})

datosv=pd.read_csv("cogotascloros.csv",sep=",")
datosv['date'] = datosv['date'].map(lambda x: str(x)[:-9])
join=datosv.set_index('date').join(datos.set_index('fechas'))
join.dropna()
#clors=[2.64,8.11,2.93,47.03,8.45,7.23,18.27,38.09,25.50,18.85]

#datosnub=datos[datos.nubes<15]
#Corrijo los valores anómalos debidos a la ineficiencia de mi capa de nubes
#a la hora de filtrar neblinas.
#datosnubclor=datosnub[datosnub.cloros<0.5]
"""
misdatos=datosnubclor[0:10]["cloros"]
mispapers=datosnubclor[0:10]["papers"]
plt.scatter(misdatos,clors)
plt.scatter(mispapers,clors)

regr = linear_model.LinearRegression()
xec2=np.array(misdatos).tolist()
papers=np.array(mispapers).tolist()

df=pd.DataFrame({'1':clors,'2':xec2,'3':papers})

df.to_csv('cloros.csv')
"""