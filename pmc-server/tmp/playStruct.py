import json
import pickle
import numpy

variableStandardKeys = ["id", "name", "type", "description", "value", "numberOfElements", "isLibrary", "isLiveVariable", "isStruct"]

def printVariable(variableJSon, fullVariableName = "", idx = ""):
    isArray = isinstance(variableJSon, list)
    if (isArray):
        if idx != "":
            idx += ","
        oidx = idx
        for k, member in enumerate(variableJSon):
            idx = oidx + str(k)
            printVariable(member, fullVariableName, idx)
    else:
        isLibrary = ((variableJSon["isLibrary"] == "true") or (variableJSon["isLibrary"] == True))
        isLiveVariable = ((variableJSon["isLiveVariable"] == "true") or (variableJSon["isLiveVariable"] == True))
        isStruct = ((variableJSon["isStruct"] == "true") or (variableJSon["isStruct"] == True))
        variable = {
            "id": variableJSon["name"],
            "name": variableJSon["name"],
            "type": variableJSon["type"],
            "description": variableJSon["description"],
            "value": pickle.dumps(variableJSon["value"]),
            "numberOfElements": pickle.dumps(variableJSon["numberOfElements"]),
            "isLibrary": isLibrary,
            "isLiveVariable": isLiveVariable,
            "isStruct": isStruct 
        }
        if (idx != ""):
            variable["id"] = idx
        if (fullVariableName != ""):
            variable["id"] = fullVariableName + "@" + variable["id"]
        if (isStruct):
            oVariableId = variable["id"]
            for memberId in variableJSon.keys():
                if (memberId not in variableStandardKeys):
                    member = variableJSon[memberId]
                    memberIsArray = isinstance(member, list)
                    memberIsArrayAnonymous = False
                    if (memberIsArray):
                        memberIsArrayAnonymous = (memberId == "privateVec")
                        if (memberIsArrayAnonymous):
                            variable["id"] = oVariableId 
                        else:
                            variable["id"] = oVariableId + "@" + memberId
                        numberOfDimensions = list(numpy.shape(member))
                    printVariable(member, variable["id"])
        print variable



jsonFileName = "/home/aneto/Projects/pmc-proto/pmc-server/java2json/Plant55A0.json"
with open(jsonFileName) as jsonFile:
    plantVariablesDBJSon = json.load(jsonFile)
    variablesJSon = plantVariablesDBJSon["variables"]
    for var in variablesJSon:
        printVariable(var)

