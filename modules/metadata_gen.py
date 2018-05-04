import xml.etree.cElementTree as ET

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
    ET.SubElement(dataset,"title").text="Datos de temperatura media en enero"
    
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
    tablaDatos=ET.SubElement(dataset,"dataTable")
    ET.SubElement(tablaDatos,"FileName").text=title+".csv"

    #--Attribute list
    atributoLista=ET.SubElement(tablaDatos,"attributeList")
    atributoFecha=ET.SubElement(atributoLista,"attributeName",id="Date")
    ET.SubElement(atributoFecha,"name").text="Date"
    ET.SubElement(atributoFecha,"formatString").text="YYYY-MM-DD"
    atributoTemp=ET.SubElement(atributoLista,"attributeName",id="Tmed")
    ET.SubElement(atributoTemp,"attributeName").text="Temperature"
    ET.SubElement(atributoTemp,"Unidadades").text="C"
    tree = ET.ElementTree(eml)

    #Escribimos los datos en un archivo
    tree.write(title+".xml",encoding='UTF-8', xml_declaration=True)
    #print(tree)

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
    ET.SubElement(dataset,"title").text="Datos de temperatura media en enero"
    
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
    tablaDatos=ET.SubElement(dataset,"dataTable")
    ET.SubElement(tablaDatos,"NombreArchivo").text="pruebaEstaciones.csv"

    #--Attribute list
    atributoLista=ET.SubElement(tablaDatos,"attributeList")
    atributoFecha=ET.SubElement(atributoLista,"attributeName",id="Date")
    ET.SubElement(atributoFecha,"name").text="Date"
    ET.SubElement(atributoFecha,"formatString").text="YYYY-MM-DD"
    atributoTemp=ET.SubElement(atributoLista,"attributeName",id="Tmed")
    ET.SubElement(atributoTemp,"attributeName").text="Temperature"
    ET.SubElement(atributoTemp,"Unidadades").text="C"
    tree = ET.ElementTree(eml)

    #Escribimos los datos en un archivo
    tree.write(title+".xml",encoding='UTF-8', xml_declaration=True)
    #print(tree)
