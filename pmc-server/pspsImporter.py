#!/usr/bin/python
"""Imports a list of variables from a json file into the backend database.
"""

import argparse
import json
#To manage the xml
from xml.etree import ElementTree
from xml.dom import minidom
from lxml import etree
#To manage the multi-dimensional numberOfElements
import numpy

#Private keys that cannot be used as member names in structures
variableStandardKeys = ["id", "name", "type", "description", "value", "numberOfElements", "isLiveVariable", "isStruct", "validation", "isLibrary"]

def isFirstIndexOfArray(variableId):
    varLen = len(variableId)
    isFirstIndex = True
    atFound = False
    i = 1
    while ((i <= varLen) and (isFirstIndex) and (not atFound)):
        ch = variableId[-i]
        isFirstIndex = ((ch == '0') or (ch == ',') or (ch == '@'))
        atFound = (ch == '@')
        i = i + 1
    return (isFirstIndex, variableId[0:-i+1])

def convertType(variableType):
    toReturn = "recordString"
    if (variableType == "float"):
        toReturn = "recordDouble"
    elif (variableType == "float32"):
        toReturn = "recordDouble"
    elif (variableType == "double"):
        toReturn = "recordDouble"
    elif (variableType == "float64"):
        toReturn = "recordDouble"
    elif (variableType == "string"):
        toReturn = "recordString"
    return toReturn

def importVariable(variableJSon, xmlParent, fullVariableName = "", idx = "", dimensions = []):
    """Recursive function which adds a variable to the database.

    This function supports the addition of multi-dimensional structured types to the database, where each member is separated by a @ sign.
    The indexes are separated by commas so that element [3][2][4] will have idx=3,2,4
    """

    isArray = isinstance(variableJSon, list)
    if (isArray):
        if idx != "":
            idx += ","
        oidx = idx
        for k, member in enumerate(variableJSon):
            idx = oidx + str(k)
            importVariable(member, xmlParent, fullVariableName, idx)
    else:
        isLiveVariable = ((variableJSon["isLiveVariable"] == "true") or (variableJSon["isLiveVariable"] == True))
        isStruct = ((variableJSon["isStruct"] == "true") or (variableJSon["isStruct"] == True))
        if (len(dimensions) == 0):
            numberOfElements = variableJSon["numberOfElements"]
        else:
            numberOfElements = dimensions
        variable = {
            "id": variableJSon["name"],
            "name": variableJSon["name"],
            "type": variableJSon["type"],
            "description": variableJSon["description"],
            "value": variableJSon["value"],
            "numberOfElements": variableJSon["numberOfElements"],
            "isLiveVariable": isLiveVariable,
            "isStruct": isStruct 
        }
        if (idx != ""):
            xmlFolder = ElementTree.SubElement(xmlParent, "folder") 
            xmlFolderName = ElementTree.SubElement(xmlFolder, "name")
            xmlFolderName.text = idx
            xmlParent = xmlFolder
        if (fullVariableName != ""):
            if (idx != ""):
               fullVariableName = fullVariableName + "@" + idx 
            fullVariableName = fullVariableName + "@" + variable["id"]

        if (isStruct):
            xmlFolders = ElementTree.SubElement(xmlParent, "folders") 
            for memberId in variableJSon.keys():
                if (memberId not in variableStandardKeys):
                    dimensions = []
                    member = variableJSon[memberId]
                    memberIsArray = isinstance(member, list)
                    if (fullVariableName == ""):
                        variableId = variable["id"]
                    else:
                        variableId = fullVariableName
                    if (memberIsArray):
                        xmlParentNext = xmlFolders
                        dimensions = list(numpy.shape(member))
                        importVariable(member, xmlParentNext, variableId, "", dimensions)
                    else:
                        memberIsStruct = ((member["isStruct"] == "true") or (member["isStruct"] == True))
                        if (memberIsStruct):
                            xmlFolder = ElementTree.SubElement(xmlFolders, "folder") 
                            xmlFolderName = ElementTree.SubElement(xmlFolder, "name")
                            xmlFolderName.text = member["name"]
                            xmlParentNext = xmlFolder
                        else:
                            xmlParentNext = xmlParent.find("records")
                            if (xmlParentNext == None):
                                xmlParentNext = ElementTree.SubElement(xmlParent, "records") 
                        importVariable(member, xmlParentNext, variableId, "", dimensions)
        else:
            xmlRecords = xmlParent
            if (xmlRecords.tag != "records"):
                xmlRecords = ElementTree.SubElement(xmlParent, "records") 
            numberOfElements = variable["numberOfElements"][0]
            xmlRecord = ElementTree.SubElement(xmlRecords, "record", {"xsi:type": convertType(variable["type"]), "size": str(numberOfElements)})
            xmlRecordName = ElementTree.SubElement(xmlRecord, "name")
            if (fullVariableName == ""):
                fullVariableName = variable["name"]
            xmlRecordName.text = fullVariableName 
            xmlRecordAlias = ElementTree.SubElement(xmlRecord, "alias")
            xmlRecordAlias.text = variable["description"]
            xmlRecordDescription = ElementTree.SubElement(xmlRecord, "description")
            xmlRecordDescription.text = variable["description"]
            xmlRecordOrigin = ElementTree.SubElement(xmlRecord, "origin")
            xmlRecordValues = ElementTree.SubElement(xmlRecord, "values")
            i = 0
            #I'm not sure if multi-dimensional arrays are supported... 
            value = variable["value"]
            if (len(value) > 0):
                value = value[0]
            while (i < numberOfElements):
                if (i < len(value)):
                    xmlRecordValue = ElementTree.SubElement(xmlRecordValues, "value")
                    xmlRecordValue.text = str(value[i])
                i = i + 1

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    roughStr = ElementTree.tostring(elem, 'utf-8')
    reparsed = etree.fromstring(roughStr)
    return etree.tostring(reparsed, pretty_print=True)

def importVariables(jsonFileName, xmlFileName, plantName, version):
    """For every json variable in the "variables" array import the variable into the database.
    """

    configurationContainer = ElementTree.Element("configurationContainer", {"xmlns":"http://www.iter.org/CODAC/PlantSystemConfig/2014", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance"})
    xmlSchemaVersion = ElementTree.SubElement(configurationContainer, "schemaVersion")
    xmlSchemaVersion.text = "1.2"
    xmlVersion = ElementTree.SubElement(configurationContainer, "version")
    xmlVersion.text = version
    xmlSddVersion = ElementTree.SubElement(configurationContainer, "sddVersion")
    xmlSddVersion.text = "1"
    xmlConfigurationContainerName = ElementTree.SubElement(configurationContainer, "name")
    xmlConfigurationContainerName.text = "Demo"
    xmlConfigurationContainerDescription = ElementTree.SubElement(configurationContainer, "description")
    xmlConfigurationContainerDescription.text = "Demo"
    xmlPlantSystems = ElementTree.SubElement(configurationContainer, "plantSystems")
    xmlPlantSystem = ElementTree.SubElement(xmlPlantSystems, "plantSystem")
    xmlPlantSystemName = ElementTree.SubElement(xmlPlantSystem, "name")
    xmlPlantSystemName.text = plantName 
    xmlPlantSystemVersion = ElementTree.SubElement(xmlPlantSystem, "version")
    xmlPlantSystemVersion.text = "1.0"
    xmlPlantSystemDescription = ElementTree.SubElement(xmlPlantSystem, "description")
    xmlPlantSystemDescription.text = "Demo"
    xmlPlantSystemRecords = ElementTree.SubElement(xmlPlantSystem, "plantRecords")
    xmlPlantSystemFolders = ElementTree.SubElement(xmlPlantSystemRecords, "folders")

    with open(jsonFileName) as jsonFile:
        plantVariablesDBJSon = json.load(jsonFile)
        variablesJSon = plantVariablesDBJSon["variables"]
        for var in variablesJSon:
            print "Importing " + var["name"]
            xmlPlantSystemFolder = ElementTree.SubElement(xmlPlantSystemFolders, "folder")
            xmlPlantSystemFolderName = ElementTree.SubElement(xmlPlantSystemFolder, "name")
            xmlPlantSystemFolderName.text = var["name"] 
            importVariable(var, xmlPlantSystemFolder)

    xmlPlantConstraints = ElementTree.SubElement(configurationContainer, "plantConstraints")

    with open(xmlFileName, "w") as xmlFile:
#        xmlFile.write(ElementTree.tostring(xmlParent))
        xmlFile.write(prettify(configurationContainer))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Import plant variables from a json file to the backend database")
    parser.add_argument("-p", "--plant", default="", help="The plant system name")
    parser.add_argument("-f", "--jsonfile", required=True, help="The input json filename")
    parser.add_argument("-x", "--xmlfile", required=True, help="The output xml filename")
    parser.add_argument("-v", "--version", required=True, help="The configuration container version")

    args = parser.parse_args()

    importVariables(args.jsonfile, args.xmlfile, args.plant, args.version)

