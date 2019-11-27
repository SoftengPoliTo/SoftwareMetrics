#!/usr/bin/env python3
# -*- coding: utf-8 -*-
    
import json
from xml.dom import minidom

def mi_tool_output_reader(xmlOutputFilePath):
    
    perFunctionList=[]
    perFunctionRes=[]
    
    xmlDoc = minidom.parse( xmlOutputFilePath )
    measures = xmlDoc.getElementsByTagName('measure')
    for measure in measures:
        if measure.getAttribute('type') == "Function":
            labels = measure.getElementsByTagName("label")
            for label in labels:
                perFunctionList.append( label.firstChild.nodeValue )
            
            items = measure.getElementsByTagName("item")
            for item in items:
                values=item.getElementsByTagName("value")
                i=0
                perFunctionValues = {}
                for value in values:
                    if perFunctionList[i] == "Maintainability":
                        #To have the standard MI formula
                        perFunctionValues[ perFunctionList[i] ] = str(int( int(value.firstChild.nodeValue) * 171/100))
                    else:
                        perFunctionValues[ perFunctionList[i] ] = value.firstChild.nodeValue
                    i+=1
                
                name=item.getAttribute("name")
                funcName    = name[ 0 : name.find("(...) at ") ] + "(...)"
                lineNumber  = name[ name.rfind(':') +1 : ]
                fileIn      = name[ name.find("(...) at ") +9 : name.rfind(':') -1 ]
                
                perFunctionRes.append( ( fileIn, funcName, lineNumber , perFunctionValues ) )
    
    return perFunctionRes

#mi_tool_output_reader("output_mi_tool.xml")

def tokei_output_reader(jsonOutputFilePath):
    
    with open(jsonOutputFilePath, 'r') as tokei_json:
        tokeiOut=json.load(tokei_json)
    tokeiOut.get('inner')
    return "TODO"

def CCCC_output_reader(ccccxml_OutputFilePath):
    perFunctionRes=[]
    
    with open(ccccxml_OutputFilePath, 'r') as cccc_file:
        ccccXml = minidom.parse(cccc_file)
    
    proj = ccccXml.getElementsByTagName("CCCC_Project")
    modules = proj[0].getElementsByTagName("oo_design")[0].getElementsByTagName("module")
    for module in modules:
        moduleName = module.getElementsByTagName("name")[0].firstChild.nodeValue
        
        WMC = module.getElementsByTagName("weighted_methods_per_class_unity")[0].getAttribute("value")
        DIT = module.getElementsByTagName("depth_of_inheritance_tree")[0].getAttribute("value")
        NOC = module.getElementsByTagName("number_of_children")[0].getAttribute("value")
        CBO = module.getElementsByTagName("coupling_between_objects")[0].getAttribute("value")
        
        # TODO: Mancanti:
        # RFC = module.getElementsByTagName("")[0].getAttribute("value")
        # LCOM= module.getElementsByTagName("")[0].getAttribute("value")
        ####
        #CC = module.getElementsByTagName("McCabes_cyclomatic_complexity")[0].firstChild.nodeValue
        #LOC = module.getElementsByTagName("lines_of_code")[0].firstChild.nodeValue
        #CLOC =module.getElementsByTagName("lines_of_comment")[0].firstChild.nodeValue
        
        with open(moduleName + ".xml", 'r') as moduleFile:
            moduleXml = minidom.parse(moduleFile)
        
        CC_module = moduleXml.getElementsByTagName("module_summary")[0].getElementsByTagName("McCabes_cyclomatic_complexity")[0].getAttribute("value")
        memberFunctions = moduleXml.getElementsByTagName("procedural_detail")[0].getElementsByTagName("member_function")
        
        ListOfmemberFunctions=[]
        for memberFunction in memberFunctions:
            memberFunctionName = memberFunction.getElementsByTagName("name")[0].firstChild.nodeValue
            fileIn = memberFunction.getElementsByTagName("source_reference")[0].getAttribute("file")
            lineNumber = memberFunction.getElementsByTagName("source_reference")[0].getAttribute("line")
            memberFunctionCC = memberFunction.getElementsByTagName("McCabes_cyclomatic_complexity")[0].getAttribute("value")
            
            perFunctionValues={}
            perFunctionValues["functionName"] = memberFunctionName
            perFunctionValues["lineNumber"] = lineNumber
            perFunctionValues["functionCC"] = memberFunctionCC
            ListOfmemberFunctions.append(perFunctionValues)
        
        perModuleMetrics={}
        perModuleMetrics["CC"]  = CC_module
        perModuleMetrics["WMC"] = WMC
        perModuleMetrics["DIT"] = DIT
        perModuleMetrics["NOC"] = NOC
        perModuleMetrics["CBO"] = CBO
        
        perFunctionRes.append( ( fileIn, moduleName, perModuleMetrics, ListOfmemberFunctions ) )
    
    return perFunctionRes
            
    # cccc.xml -> procedural_summary->module : prendi lista modules
    # carica ogni file *modulo*
    # Per Ogni modulo, prendere TUTTE le funzioni ==> Calcola WMC!x\
    # 
    #