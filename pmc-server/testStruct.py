#!/usr/bin/python
import argparse
import os
import pickle
import time
import json
import dataset
import numpy

db = dataset.connect('sqlite:////tmp/pmc-server.db')

'''
    PMC::VAR1@0
    PMC::VAR1@0@gaps

    PMC::VAR1@0@gaps@0@x1
    PMC::VAR1@0@gaps@0@x2
    PMC::VAR1@0@gaps@0@y1
    PMC::VAR1@0@gaps@0@y2

    PMC::VAR1@0@gaps@1@x1
    PMC::VAR1@0@gaps@1@x2
    PMC::VAR1@0@gaps@1@y1
    PMC::VAR1@0@gaps@1@y2

    PMC::VAR1@0@gaps@2@x1
    PMC::VAR1@0@gaps@2@x2
    PMC::VAR1@0@gaps@2@y1
    PMC::VAR1@0@gaps@2@y2
'''

def isArray(numberOfElements):
    variableIsArray = (len(numberOfElements) > 1)
    if (not variableIsArray):
        variableIsArray = (numberOfElements[0] > 1)
    return variableIsArray


def getMaxLinearIndex(numberOfElements):
    maxIdx = 1
    for i,val in enumerate(numberOfElements):
        maxIdx = maxIdx * numberOfElements[i]
    return maxIdx

def getDividers(numberOfElements):
    numberOfDimensions = len(numberOfElements)
    dividers = []
    for i, val in enumerate(numberOfElements):
        j = i
        divider = 1
        while(j < numberOfDimensions):
            divider = divider * numberOfElements[j]
            j = j + 1
        dividers.append(divider)
    dividers = dividers[1:numberOfDimensions]
    return dividers

def setAtArrayIndex(ret, variableId, value):
    idxs = variableId.split("@")[-1].split(",")
    for k, idx in enumerate(idxs):
        if (k < (len(idxs) - 1)):
            ret = ret[int(idx)]
        else:
            ret[int(idx)] = value

variables = db["variables"]
permissions = db["permissions"]
validations = db["validations"]

def getVariable(row):
    variable = row
    variable["variableId"] = variable["id"]  
    variable["isLibrary"] = (variable["isLibrary"] == 1)
    if (variable["value"] != ""):
        variable["value"] = pickle.loads(variable["value"])  
    variable["numberOfElements"] = pickle.loads(variable["numberOfElements"])  
    variable["validation"] = []  
    validation = validations.find(variable_id=variable["id"])
    for v in validation:
        variable["validation"].append({
            "description": v["description"],
            "fun": v["fun"],
            "parameters": pickle.loads(v["parameters"])
        })

    variable["permissions"] = []
    permission = permissions.find(variable_id=variable["id"])
    for p in permission:
        variable["permissions"].append(p["group_id"])
    
    return variable


def getValue(variableId):
    #statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id'" + variableId + "'"
    statement = "SELECT * FROM variables WHERE id='" + variableId + "'"
    row = variables.find_one(id=variableId)
    variableNumberOfElements = pickle.loads(row["numberOfElements"])
    variableIsArray = isArray(variableNumberOfElements) 
    variableIsStruct = row["isStruct"]
    if (variableIsStruct): 
        ret = getVariable(row)
        if (variableIsArray):
            ret = numpy.empty(variableNumberOfElements).tolist()
        #statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id LIKE '" + variableId + "@%' AND id NOT LIKE '" + variableId + "@%@%'"
        statement = "SELECT * FROM variables WHERE id LIKE '" + variableId + "@%' AND id NOT LIKE '" + variableId + "@%@%'"
        for row in db.query(statement):
            memberNumberOfElements = pickle.loads(row["numberOfElements"])
            variableId = row["id"]
            memberId = variableId.split("@")[-1]
            memberIsStruct = row["isStruct"]
            memberIsArray = isArray(memberNumberOfElements)
            if (memberIsStruct):
                if (memberIsArray):
                    appendTo = numpy.empty(memberNumberOfElements).tolist()
                    if (variableIsArray):
                        setAtArrayIndex(ret, variableId, appendTo)
                    else:
                        ret[memberId] = appendTo
                    idxStr = ""
                    maxIdx = getMaxLinearIndex(memberNumberOfElements)
                    dividers = getDividers(memberNumberOfElements)
                    numberOfDimensions = len(memberNumberOfElements)
                    idx = 0
                    i = 0
                    while i < maxIdx:
                        j = 0
                        while j < numberOfDimensions:
                            dividerIdx = j % numberOfDimensions
                            if (dividerIdx != (numberOfDimensions - 1)):
                                idx = i / dividers[dividerIdx]
                                idx = idx % memberNumberOfElements[j]
                            else:
                                idx = i % memberNumberOfElements[dividerIdx]

                            if (dividerIdx == 0):
                                idxStr = str(idx)
                            else:
                                idxStr = idxStr + "," + str(idx)
        
                            if (dividerIdx == (numberOfDimensions - 1)):
                                variableIdIdx = variableId + "@" + idxStr
                                setAtArrayIndex(appendTo, variableIdIdx, getValue(variableIdIdx))
                                idxStr = ""
                            j = j + 1
                        i = i + 1
                else:
                    if (variableIsArray):
                        setAtArrayIndex(ret, variableId, getValue(variableId))
                    else:
                        ret[memberId] = getValue(variableId)
            else:
                if (variableIsArray):
                    #setAtArrayIndex(ret, variableId, pickle.loads(row["value"]))
                    setAtArrayIndex(ret, variableId, getVariable(row))
                else:
                    #ret[memberId] = pickle.loads(row["value"])
                    ret[memberId] = getVariable(row)       
    else:
        #return pickle.loads(row["value"]) 
        return getVariable(row) 
    return ret

if __name__ == "__main__":
    #NUMBER OF ELEMENTS = [DIM1 DIM2 DIM3...]
#    v = getValue("55A0::VAR1")
#    print v
    v = getValue("55A0::VAR4")
#    print v
#    v = json.dumps(getValue("55A0::VAR5"))
    print json.dumps(v)
"""
    print "=================================================================\n\n"
    v = getValue("PLANT3::VAR1@gaps")
    print v
    print "=================================================================\n\n"
    v = getValue("PLANT3::VAR1@gaps@0")
    print v
    print "=================================================================\n\n"
    v = getValue("PLANT3::VAR1@gaps@0@x1")
    print v
    print "=================================================================\n\n"
    #print json.dumps(v)
"""
'''
                    i = 0
                    j = 0
                    idxStr = ""
                    maxIdx = getMaxLinearIndex(numberOfElements)
                    dividers = getDividers(numberOfElements)
                    numberOfDimensions = len(numberOfElements)
                    idx = 0
                    while i < maxIdx:
                        while j < numberOfDimensions:
                            dividerIdx = j % numberOfDimensions
                            if (dividerIdx != (numberOfDimensions - 1)):
                                idx = i / dividers[dividerIdx]
                                idx = idx % numberOfElements[j]
                            else:
                                idx = i % numberOfElements[dividerIdx]

                            if (dividerIdx == 0):
                                idxStr = str(idx)
                            else:
                                idxStr = idxStr + "," + str(idx)
        
                            if (dividerIdx == (numberOfDimensions - 1)):
                                variableIdIdx = variableId + "@" + idxStr
                                print variableIdIdx
                                appendTo.append(getValue(variableIdIdx))
                                idxStr = ""
                            j = j + 1
                        i = i + 1
                    #while(idx < numberOfElements):
                    #    variableIdIdx = variableId + "@" + str(idx)
                    #    appendTo.append(getValue(variableIdIdx))
                    #    idx = idx + 1
'''                  

