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

import xml.etree.cElementTree as ET
import xmltodict 
import os
import json
import requests

from wq_modules import config

def metadata_gen(title,dateIni,dateEnd,geographicDesc,westBounding,eastBounding,northBounding,southBounding,params):
    
    #EML-XML Header
    ET.register_namespace('eml',"eml://ecoinformatics.org/eml-2.1.1") #some name
    eml = ET.Element("{eml://ecoinformatics.org/eml-2.1.1}eml",system="knb" )
    #eml = ET.Element("eml:eml",system="knb",xmlns="eml://ecoinformatics.org/eml-2.1.1")
    
    #-Access
    acceso = ET.SubElement(eml, "access", authSystem="knb", order="allowFirst")
    permiso=ET.SubElement(acceso,"allow")
    ET.SubElement(permiso,"principal").text="public"
    ET.SubElement(permiso,"permission").text="read"
    

    #-Dataset Module
    dataset=ET.SubElement(eml,"dataset")
    ET.SubElement(dataset,"title").text=title
    
    #--Coverage
    coverage=ET.SubElement(dataset,"coverage")
    
    #---Geographic Coverage
    coverageG=ET.SubElement(coverage,"geographicCoverage",id='id')
    ET.SubElement(coverageG,"geographicDescription").text=geographicDesc
    ET.SubElement(coverageG,"westBoundingCoordinate").text=westBounding
    ET.SubElement(coverageG,"eastBoundingCoordinate").text=eastBounding
    ET.SubElement(coverageG,"northBoundingCoordinate").text=northBounding
    ET.SubElement(coverageG,"southBoundingCoordinate").text=southBounding

    #---Temporal Coverage
    coverageT=ET.SubElement(coverage,"temporalCoverage")
    #---SingleData
    #----TODO
    #---rangeOfDates
    rangeOfDates=ET.SubElement(coverageT,"rangeOfDates")
    #----beginDate
    ET.SubElement(ET.SubElement(rangeOfDates,"beginDate"),"calendarDate").text=dateIni
    #---endDate
    ET.SubElement(ET.SubElement(rangeOfDates,"endDate"),"calendarDate").text=dateEnd
   
    #--Dataset type
    fileFormat = "csv"
    if fileFormat == "csv":
        
        #filename.split(".")[-1]
        dataTable=ET.SubElement(dataset,"dataTable")
        ET.SubElement(dataTable,"FileName").text=title+".csv"
        dataTable = file_block_csv(title,params,dataTable)

    tree = ET.ElementTree(eml)

    #Escribimos los datos en un archivo or onedata attachement

    tree.write(config.datasets_path + '/' + geographicDesc + '/' + title+".xml",encoding='UTF-8', xml_declaration=True)
    
    if (config.onedata_mode == 1):
        try:
            token = os.environ['ONECLIENT_AUTHORIZATION_TOKEN']
        except KeyError:
            token = 'MDAxNWxvY2F00aW9uIG9uZXpvbmUKMDAzMGlkZW500aWZpZXIgOTAwNGNlNzBiYWQyMTYzYzY1YWY4NTNhZjQyMGJlYWEKMDAxYWNpZCB00aW1lIDwgMTU4MzkxODYyOQowMDJmc2lnbmF00dXJlICmASYmuGx6CSPHwkf3s9pXW2szUqJPBPoFEXIKOZ2L00Cg'
        header_json = {'X-Auth-Token': token, 'Content-type' : 'application/json'}
        try:
            print(config.onedata_url+config.onedata_api+'metadata/'+ config.onedata_space + '/' + geographicDesc + '/' + title)
            print(eml_to_json(config.datasets_path + '/' + geographicDesc + '/' + title+".xml"))
            r = requests.put(config.onedata_url+config.onedata_api+'metadata/json/'+ config.onedata_space + '/' + geographicDesc + '/' + title,headers=header_json,data=eml_to_json(title+".xml"))
            print("Metadata attachement: %i" % r.status_code)
            os.remove(title+".xml")
        except requests.exceptions.RequestException as e:
            print(e)
    print(tree)

def metadata_gen(title,dateIni,dateEnd,geographicDesc,westBounding,northBounding,params):
    
    #EML-XML Header
    ET.register_namespace('eml',"eml://ecoinformatics.org/eml-2.1.1") #some name
    eml = ET.Element("{eml://ecoinformatics.org/eml-2.1.1}eml",system="knb" )
    #eml = ET.Element("eml:eml",system="knb",xmlns="eml://ecoinformatics.org/eml-2.1.1")
    
    #-Access
    acceso = ET.SubElement(eml, "access", authSystem="knb", order="allowFirst")
    permiso=ET.SubElement(acceso,"allow")
    ET.SubElement(permiso,"principal").text="public"
    ET.SubElement(permiso,"permission").text="read"
    

    #-Dataset Module
    dataset=ET.SubElement(eml,"dataset")
    ET.SubElement(dataset,"title").text=title
    
    #--Coverage
    coverage=ET.SubElement(dataset,"coverage")
    
    #---Geographic Coverage
    coverageG=ET.SubElement(coverage,"geographicCoverage",id='id')
    ET.SubElement(coverageG,"geographicDescription").text=geographicDesc
    ET.SubElement(coverageG,"westBoundingCoordinate").text=westBounding
    ET.SubElement(coverageG,"eastBoundingCoordinate").text=westBounding
    ET.SubElement(coverageG,"northBoundingCoordinate").text=northBounding
    ET.SubElement(coverageG,"southBoundingCoordinate").text=northBounding

    #---Temporal Coverage
    coverageT=ET.SubElement(coverage,"temporalCoverage")
    #---SingleData
    #----TODO
    #---rangeOfDates
    rangeOfDates=ET.SubElement(coverageT,"rangeOfDates")
    #----beginDate
    ET.SubElement(ET.SubElement(rangeOfDates,"beginDate"),"calendarDate").text=dateIni
    #---endDate
    ET.SubElement(ET.SubElement(rangeOfDates,"endDate"),"calendarDate").text=dateEnd
   
    #--Dataset type
    fileFormat = "csv"
    if fileFormat == "csv":

        #filename.split(".")[-1]
        dataTable=ET.SubElement(dataset,"dataTable")
        ET.SubElement(dataTable,"FileName").text=title
        dataTable = file_block_csv(title,params,dataTable)

    tree = ET.ElementTree(eml)

    #Escribimos los datos en un archivo or onedata attachement
    tree.write(config.datasets_path + '/' + geographicDesc + '/' + title+".xml",encoding='UTF-8', xml_declaration=True)
    
    if (config.onedata_mode == 1):
        try:
            token = os.environ['ONECLIENT_AUTHORIZATION_TOKEN']
        except KeyError:
            token = 'MDAxNWxvY2F00aW9uIG9uZXpvbmUKMDAzMGlkZW500aWZpZXIgOTAwNGNlNzBiYWQyMTYzYzY1YWY4NTNhZjQyMGJlYWEKMDAxYWNpZCB00aW1lIDwgMTU4MzkxODYyOQowMDJmc2lnbmF00dXJlICmASYmuGx6CSPHwkf3s9pXW2szUqJPBPoFEXIKOZ2L00Cg'
        header_json = {'X-Auth-Token': token, 'Content-type' : 'application/json'}
        try:
            
            print (config.onedata_url+config.onedata_api+'metadata/json/'+ config.onedata_space + '/' + geographicDesc + '/' + title)
            #print(eml_to_json(config.datasets_path + '/' + geographicDesc + '/' + title+".xml"))
            js = eml_to_json(config.datasets_path + '/' + geographicDesc + '/' + title+".xml")
            met = json.loads(js)
            print(json.dumps(met, indent=1, sort_keys=True))
            r = requests.put(config.onedata_url+config.onedata_api+'metadata/'+ config.onedata_space + '/' + geographicDesc + '/' + title,headers=header_json,data=eml_to_json(config.datasets_path + '/' + geographicDesc + '/' + title+".xml"))

            print("Metadata attachement: %i" % r.status_code)
            os.remove(config.datasets_path + '/' + geographicDesc + '/' + title+".xml")
        except requests.exceptions.RequestException as e:
            print(e)
    print(tree)

def file_block_csv(title,params,parent):
    dataTable=ET.SubElement(parent,"dataTable", id=title)
    ET.SubElement(dataTable,"entityName").text=title
    phisical = ET.SubElement(dataTable,"physical")
    ET.SubElement(phisical,"objectName").text=title
    ET.SubElement(phisical,"size", unit="bytes").text="1231" #TODO
    ET.SubElement(phisical,"characterEncoding").text="ASCII"

    dataFormat = ET.SubElement(phisical,"dataFormat")
    textFormat = ET.SubElement(dataFormat,"textFormat")

    ET.SubElement(textFormat,"numHeaderLines").text="1" #TODO
    ET.SubElement(textFormat,"attributeOrientation").text="column"
    ET.SubElement(ET.SubElement(textFormat,"simpleDelimited"),"fieldDelimiter").text="\\t"

    #--Attribute list
    dataTable = attribute_block_csv(params,dataTable)
    return parent

def attribute_block_csv(params,dataTable):
    print("PARAMS")
    print(params)
    #TODO Complete
    attributeList=ET.SubElement(dataTable,"attributeList")
    for att in params:
        if att == "Date":
            attribute=ET.SubElement(attributeList,"attribute",id="Date")
            ET.SubElement(attribute,"attributeName").text="Date"
            ET.SubElement(attribute,"attributeDefinition").text="Date"
            ET.SubElement(attribute,"formatString").text="YYYY-MM-DD"
        
        elif att == "Temp":
            attribute=ET.SubElement(attributeList,"attribute",id="Temp")
            ET.SubElement(attribute,"attributeName").text="Temperature"
            ET.SubElement(attribute,"attributeLabel").text="Temp"
            ET.SubElement(attribute,"attributeDefinition").text="Temperature" 
            ET.SubElement(attribute,"standardUnit").text="Celsius"

        elif att == "Wind_Speed":
            attribute=ET.SubElement(attributeList,"attribute",id="Wind_Speed")
            ET.SubElement(attribute,"attributeName").text="Wind_Speed"
            ET.SubElement(attribute,"attributeLabel").text="Wind_Speed"
            ET.SubElement(attribute,"attributeDefinition").text="Average wind speed"
            ET.SubElement(attribute,"standardUnit").text="m/s"

        elif att == "Wind_Dir":
            attribute=ET.SubElement(attributeList,"attribute",id="Wind_Dir")
            ET.SubElement(attribute,"attributeName").text="Wind_Dir"
            ET.SubElement(attribute,"attributeLabel").text="Wind_Dir"
            ET.SubElement(attribute,"attributeDefinition").text="Wind direction"
            ET.SubElement(attribute,"standardUnit").text="degrees"
        
        elif att == "ID":
            attribute=ET.SubElement(attributeList,"attribute",id="ID")
            ET.SubElement(attribute,"attributeName").text="ID"
            ET.SubElement(attribute,"attributeLabel").text="ID"
            ET.SubElement(attribute,"storageType").text="string"

    return dataTable

def eml_to_json(xml_file):
    with open(xml_file, "rb") as f:
        o = xmltodict.parse(f, xml_attribs=True)
    result = json.dumps(o)
    return result
