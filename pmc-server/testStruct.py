#!/usr/bin/python
import argparse
import os
import pickle
import time
import json
import dataset

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

def getValue(variableId):
    variables = db["variables"]
    statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id'" + variableId + "'"
    row = variables.find_one(id=variableId)
    numberOfElements = int(row["numberOfElements"])
    variableIsArray = (numberOfElements > 1)
    variableIsStruct = row["isStruct"]
    
    if (variableIsStruct): 
        ret = {}
        if (variableIsArray):
            ret = []
        statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id LIKE '" + variableId + "@%' AND id NOT LIKE '" + variableId + "@%@%'"
        for row in db.query(statement):
            numberOfElements = int(row["numberOfElements"])
            variableId = row["id"]
            memberId = variableId.split("@")[-1]
            memberIsStruct = row["isStruct"]
            memberIsArray = (numberOfElements > 1)
            if (memberIsStruct):
                if (memberIsArray):
                    idx = 0
                    if (variableIsArray):
                        ret.append([])
                        appendTo = ret[0]
                    else:
                        ret[memberId] = []
                        appendTo = ret[memberId]
                    
                    while(idx < numberOfElements):
                        variableIdIdx = variableId + "@" + str(idx)
                        appendTo.append(getValue(variableIdIdx))
                        idx = idx + 1
                else:
                    if (variableIsArray):
                        ret.append(getValue(variableId))
                    else:
                        ret[memberId] = getValue(variableId)
            else:
                if (variableIsArray):
                    ret.append(pickle.loads(row["value"]))
                else:
                    ret[memberId] = pickle.loads(row["value"])
       
    else:
        return pickle.loads(row["value"]) 
    return ret

if __name__ == "__main__":
    #NUMBER OF ELEMENTS = [DIM1 DIM2 DIM3...]
    v = getValue("PLANT3::VAR1")
    print v
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

