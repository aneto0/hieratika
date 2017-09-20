import argparse

import Queue

import threading

import epics
from epics import caget, caput, camonitor

import time

import json

from flask import Flask, Response, request


app = Flask(__name__, static_url_path="")

#list of variables to monitor
#plantVariablesToMonitor = [epics.PV("PMC::TEST::VAR1"), epics.PV("PMC::TEST::VAR2"), epics.PV("PMC::TEST::VAR3"), epics.PV("PMC::TEST::VAR4")]

#live database simulating the plant
plantVariablesDB = []

#Synchronised queue between the SSE stream_data function and the pvValueChanged. One queue per consumer thread. Should be further protected with semaphores
threadQueues = {}

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadQueues.iteritems():
        q.put((pvname, value), True)

#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamData():
    while True:
        tid = str(threading.current_thread())
        if tid not in threadQueues:
            # The first time send all the variables
            threadQueues[tid] = Queue.Queue()
            encodedPy = {"plantVariables": [ ] }
            for pv in plantVariablesDB:
                pvName = pv["name"]
                if pv["epicsPV"] == "true" and pv["library"] == "false":
                    value = str(epics.PV(pvName).get())
                else:
                    value = pv["initialValue"]
                
                pv["value"] = value
                encodedPy["plantVariables"].append({"name" : pvName, "value" : value})
            encodedJson = json.dumps(encodedPy)
        else:
            # Just monitor on change 
            monitorQueue = threadQueues[tid]
            updatedPV = monitorQueue.get(True)
            pvName = updatedPV[0]
            pvValue = updatedPV[1]
            encodedPy = {"plantVariables": [ {"name" : pvName, "value" : str(pvValue)}] }
            encodedJson = json.dumps(encodedPy)
            monitorQueue.task_done()
        yield "data: {0}\n\n".format(encodedJson)

#Gets all the pv information
@app.route("/getplantinfo")
def getplantinfo():
#    for pv in plantVariablesToMonitor:
#        pvNElements = pv.nelm
#        pvType = pv.type
#        if (pvType == "time_long"):
#            pvType = "int32"
#        elif (pvType == "time_double"):
#            pvType = "float64"
#        else:
#            pvType = "string"

#        encodedPy["pv"].append({"name" : pv.pvname, "type" : str(pvType), "numberOfElements" : str(pvNElements)})
#    encodedJson = json.dumps(encodedPy)
    encodedPy = {"variables": plantVariablesDB }
    encodedJson = json.dumps(encodedPy)
    return encodedJson
  
#Try to update the values in the plant
@app.route("/submit", methods=["POST", "GET"])
def submit():
    if (request.method == "GET"):
        print request.args
        for k in request.args:
            caput(k, request.args[k])
    return "done"

#Return the available schedules
@app.route("/getschedules")
def getschedules():
    scheduleNames = []
    with open("static/schedules.json") as jsonFile:
        schedulesJson = json.load(jsonFile)
        schedules = schedulesJson["schedules"]
        for s in schedules:
            scheduleNames.append(s["name"]);
    return json.dumps(scheduleNames)

#Return the available arrays
@app.route("/getarrays")
def getarrays():
    arrayNames = []
    with open("static/arrays.json") as jsonFile:
        arraysJson = json.load(jsonFile)
        arrays = arraysJson["arrays"]
        for a in arrays:
            varName = a["variable"]
            varArrays = a["arrays"]

            varInfo = {}
            varInfo["variable"] = varName
            varInfo["names"] = []
            for va in varArrays:
                varInfo["names"].append(va["name"])

            arrayNames.append(varInfo)
    return json.dumps({"arrays": arrayNames})

#Returns the array information associated to a given variable
@app.route("/getarray", methods=["POST", "GET"])
def getarray():
    if (request.method == "GET"):
        requestedVariable = request.args["variable"]
        requestedArrayName = request.args["arrayName"]
        with open("static/arrays.json") as jsonFile:
            arraysJson = json.load(jsonFile)
            allArrays = arraysJson["arrays"]
            for v in allArrays:
                if (v["variable"] == requestedVariable):
                    variableArrays = v["arrays"]
                    for a in variableArrays:
                        if (a["name"] == requestedArrayName):
                            values = a["values"]
                            break
                    break
    return json.dumps(values)


#Returns the variables associated to a given schedule
@app.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    if (request.method == "GET"):
        requestedSchedule = request.args["schselect"]
        with open("static/schedules.json") as jsonFile:
            schedulesJson = json.load(jsonFile)
            schedules = schedulesJson["schedules"]
            for s in schedules:
                if (s["name"] == requestedSchedule):
                    variables = s["variables"]
#                    for v in variables:
#                        if (v["isPV"] == "True"):
#                            pvName = v["name"]
#                            pvValue = v["value"]
#                            caput(pvName, pvValue)
                    break
    return json.dumps(variables)


@app.route("/stream")
def stream():
    return Response(streamData(), mimetype="text/event-stream")

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    epics.ca.find_libca()
    
    parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Server port")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    args = parser.parse_args()

    with open("plant-variables.json") as jsonFile:
        plantVariablesDBJSon = json.load(jsonFile)
        #Assume the first plant for the time being
        plantVariablesDB = plantVariablesDBJSon["plants"][0]["variables"]

    for pv in plantVariablesDB:
        if pv["epicsPV"] == "true":
            camonitor(pv["name"], None, pvValueChanged)

    app.debug = True
    app.run(threaded= True, host=args.host, port=args.port)
