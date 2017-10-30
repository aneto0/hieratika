#!/usr/bin/python
"""Imports a list of variables from a json file into the backend database.
"""

import argparse
import json
#Manage an easier integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle
#To manage the multi-dimensional numberOfElements
import numpy

#Private keys that cannot be used as member names in structures
variableStandardKeys = ["id", "name", "type", "description", "value", "numberOfElements", "isLibrary", "isLiveVariable", "isStruct", "validation"]

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

def importVariable(variableJSon, variablesDB, validationsDB, permissionsDB, groups, fullVariableName = "", idx = "", dimensions = []):
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
            importVariable(member, variablesDB, validationsDB, permissionsDB, groups, fullVariableName, idx)
    else:
        isLibrary = ((variableJSon["isLibrary"] == "true") or (variableJSon["isLibrary"] == True))
        isLiveVariable = ((variableJSon["isLiveVariable"] == "true") or (variableJSon["isLiveVariable"] == True))
        isStruct = ((variableJSon["isStruct"] == "true") or (variableJSon["isStruct"] == True))
        if (len(dimensions) == 0):
            numberOfElements = pickle.dumps(variableJSon["numberOfElements"])
        else:
            numberOfElements = pickle.dumps(dimensions)
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

        variableId = variable["id"]
        variablesDB.upsert(variable, ["id"])

        checkFirstIndexOfArray = isFirstIndexOfArray(variableId)
        if (checkFirstIndexOfArray[0]):
            #Update the array type (which was created below)
            variable = {
                "id": checkFirstIndexOfArray[1],
                "type": variableJSon["type"],
                "description": "An array of " + variableJSon["type"] + " elements"
            }
            variablesDB.upsert(variable, ["id"])

        if (isStruct):
            oVariableId = variable["id"]
            for memberId in variableJSon.keys():
                if (memberId not in variableStandardKeys):
                    dimensions = []
                    member = variableJSon[memberId]
                    memberIsArray = isinstance(member, list)
                    if (memberIsArray):
                        variableId = oVariableId + "@" + memberId
                        dimensions = list(numpy.shape(member))
                        #Declare the array (the type will be discovered later (it will be the type of the first element), see above)
                        variable = {
                            "id": variableId,
                            "numberOfElements": pickle.dumps(dimensions),
                            "name": variableId,
                            "type": "",
                            "description": "",
                            "value": "",
                            "isLibrary": False,
                            "isLiveVariable": False,
                            "isStruct": True
                        }
                        variablesDB.upsert(variable, ["id"])
                    importVariable(member, variablesDB, validationsDB, permissionsDB, groups, variableId, "", dimensions)
        if "validation" in variableJSon:
            validationsJSon = variableJSon["validation"]
            for validationJSon in validationsJSon:
                validation = {
                    "fun": validationJSon["fun"],
                    "variable_id": variableId,
                    "description": validationJSon["description"],
                    "parameters": pickle.dumps(validationJSon["parameters"])  
                }
                validationsDB.upsert(validation, ["fun", "variable_id"])
        if (groups != ""):
            permission = {
                "variable_id": variableId,
                "group_id": groups
            }
            permissionsDB.upsert(permission, ["variable_id", "group_id"])


def importVariables(jsonFileName, db, prefix = "", groups = ""):
    """For every json variable in the "variables" array import the variable into the database.
    """

    variablesDB = db["variables"]
    validationsDB = db["validations"]
    permissionsDB = db["permissions"]
    with open(jsonFileName) as jsonFile:
        plantVariablesDBJSon = json.load(jsonFile)
        variablesJSon = plantVariablesDBJSon["variables"]
        for var in variablesJSon:
            if (prefix != ""):
                var["name"] = prefix + var["name"]
            importVariable(var, variablesDB, validationsDB, permissionsDB, groups)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Import plant variables from a json file to the backend database")
    parser.add_argument("-D", "--database", default="/tmp/pmc-server.db", help="Database file location")
    parser.add_argument("-p", "--prefix", default="", help="A prefix to apply to all variable names")
    parser.add_argument("-f", "--jsonfile", required=True, help="The variable prefix")
    parser.add_argument("-g", "--group", default="", help="Comma separated group ids that have permission to change the variable value in run-time")

    args = parser.parse_args()

    db = dataset.connect("sqlite:///" + args.database)
    importVariables(args.jsonfile, db, args.prefix, args.group)

