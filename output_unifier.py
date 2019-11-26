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
                
                perFunctionRes.append( ( funcName, fileIn, lineNumber , perFunctionValues ) )
    
    return perFunctionRes

#mi_tool_output_reader("output_mi_tool.xml")

def tokei_output_reader(jsonOutputFilePath):
    
    with open(jsonOutputFilePath, 'r') as tokei_json:
        tokeiOut=json.load(tokei_json)
    tokeiOut.get('inner')
    return "TODO"

def CCCC_output_reader(ccccxml_OutputFilePath):
    with open(ccccxml_OutputFilePath, 'r') as cccc_file:
        ccccXml = minidom.parse(cccc_file)
    
    # cccc.xml -> procedural_summary->module : prendi lista modules
    # carica ogni file *modulo*
    # Per Ogni modulo, prendere TUTTE le funzioni ==> Calcola WMC!
    # 
    #