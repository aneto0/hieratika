from xml.etree import ElementTree
from xml.dom import minidom
from lxml import etree

tree = ElementTree.parse('/tmp/Plant55A0.xml')
root = tree.getroot()

ns = {"default": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
      "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

def convertVariableTypeFromXML(xmlVariableType):
    toReturn = "string"
    if (xmlVariableType == "recordDouble"):
        toReturn = "float64" 
    elif (xmlVariableType == "recordFloat"):
        toReturn = "float32" 
    elif (xmlVariableType == "recordString"):
        toReturn = "string" 
    return toReturn

def getVariable(variableName):
    path = variableName.split("@")
    r = root.find("./default:plantSystems/default:plantSystem/default:plantRecords", ns)
    for p in path[:-1]:
        r = r.find("./default:folders/default:folder[default:name='{0}']".format(p), ns)
        if (r == None):
            break
    #r = r.find("./default:records/default:record[default:name='{0}']".format(path[-1]), ns)
    #TODO this will have to be changed to the version above as the final name will only be path[-1] and not the full path
    r = r.find("./default:records/default:record[default:name='{0}']".format(variableName), ns)
    variable = {}
    if (r is not None):
        variable["type"] = convertVariableTypeFromXML(r.attrib["{" + ns["xsi"] + "}type"])
        variable["numberOfElements"] = "[" + r.attrib["size"] + "]"
        variable["name"] = r.find("./default:name", ns).text
        variable["id"] = variable["name"]
        variable["description"] = r.find("./default:description", ns).text
        values = r.findall(".//default:value", ns)
        valueStr = "["
        for v in values[:-1]:
            valueStr += v.text + ","
        valueStr += values[-1].text + "]"
        variable["value"] = valueStr

    print variable
    
getVariable("MLFS@AA@M1007@angle")

