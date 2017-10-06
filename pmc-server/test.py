import argparse
import Queue
import threading
import epics
from epics import caget, caput, camonitor
import time
import json
from flask import Flask, Response, request, send_from_directory

#Manage easy integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

app = Flask(__name__, static_url_path="")

#TODO this will have to be purged from time to time...
threadDBs = {}
def getDB():
    tid = str(threading.current_thread())
    if tid not in threadDBs:
        threadDBs[tid] = dataset.connect('sqlite:////tmp/pmc-server.db')
    return threadDBs[tid]
    
#Synchronised queue between the SSE stream_data function and the pvValueChanged. One queue per consumer thread. Should be further protected with semaphores
#TODO this will have to be cleared from time to time
threadQueues = {}

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadQueues.iteritems():
        pvname = pvname.split("::")
        plantId = pvname[0]
        variableId = pvname[1]
        q.put((plantId, variableId, value), True)

def updatePlantVariablesDB(plantId, variableId, variableValue):
    db = getDB()
    plantVariables = db["plant_variables"]
    row = plantVariables.find_one(id=pvName,plant_id=plantId)
    if (row is not None):
        row["value"] = pickle.dumps(pvValue);
        plantVariables.upsert(row, ["id"])

#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamData():
    try:
        while True:
            db = getDB()
            tid = str(threading.current_thread())
            plantVariables = db["plant_variables"]
            if tid not in threadQueues:
                # The first time send all the variables
                threadQueues[tid] = Queue.Queue()
                encodedPy = {"plantVariables": [ ] }
                for plantVariable in plantVariables:
                    variableId = plantVariable["id"]
                    plantId = plantVariable["plant_id"]
                    value = pickle.loads(plantVariable["value"])
                    encodedPy["plantVariables"].append({"variableId" : variableId, "plantId" : plantId, "value" : value})
                encodedJson = json.dumps(encodedPy)
            else:
                # Just monitor on change 
                monitorQueue = threadQueues[tid]
                updatedPV = monitorQueue.get(True)
                plantId = updatedPV[0]
                variableId = updatedPV[1]
                encodedPy = {"plantVariables": [ {"variableId" : variableId, "plantId" : plantId, "value" : pvValue}] }
                encodedJson = json.dumps(encodedPy)
                monitorQueue.task_done()
            yield "data: {0}\n\n".format(encodedJson)
    except Exception:
        print "Exception ignored"
        #ignore

#Gets all the pv information
@app.route("/getplantinfo")
def getplantinfo():
    db = getDB()
    plantVariables = db["plant_variables"]
    validations = db["validations"]
    #TODO. THIS WILL HAVE TO COME HAS PART OF THE REQUEST!
    plantId = "PLANT1"
    encodedPy = {"variables": [] }
    for plantVariable in plantVariables:
        plantVariable["plantId"] = plantVariable["plant_id"]  
        plantVariable["variableId"] = plantVariable["id"]  
        plantVariable["library"] = (plantVariable["library"] == 1)
        plantVariable["initialValue"] = pickle.loads(plantVariable["initialValue"])  
        plantVariable["value"] = pickle.loads(plantVariable["value"])  
        plantVariable["numberOfElements"] = pickle.loads(plantVariable["numberOfElements"])  
        plantVariable["validation"] = []  
        validation = validations.find(plant_id=plantVariable["plant_id"], variable_id=plantVariable["id"])
        for v in validation:
            plantVariable["validation"].append({
                "description": v["description"],
                "fun": v["fun"],
                "parameters": pickle.loads(v["parameters"])
            })
        encodedPy["variables"].append(plantVariable) 
    encodedJson = json.dumps(encodedPy)
    return encodedJson
  
#Try to update the values in the plant
@app.route("/submit", methods=["POST", "GET"])
def submit():
    if (request.method == "GET"):
        updateJSon = request.args["update"]
        jSonUpdateVariables = json.loads(updateJSon)
        for varName in jSonUpdateVariables:
            newValue = jSonUpdateVariables[varName]
            varName = varName.split("::")
            if len(varName) == 2:
                plantId = varName[0]
                variableId = varName[1]
                updatePlantVariablesDB(plantId, variableId, newValue)
                #Warn others that the plant values have changed!
                for k, q in threadQueues.iteritems():
                    q.put((plantId, variableId, newValue), True)

            #caput(k, request.args[k])
    return "done"

#Return the available schedules
@app.route("/getschedules")
def getschedules():
    db = getDB()
    tableSchedules = db["schedules"]
    scheduleNames = []
    for s in tableSchedules:
        scheduleNames.append(s["id"]);
    return json.dumps(scheduleNames)

#Return the available libraries
@app.route("/getlibraries")
def getlibraries():
    db = getDB()
    tableLibraries = db["libraries"]
    librariesNames = {}
    for library in tableLibraries:
        plantId = library["plant_id"]
        variableId = library["variable_id"]
        variable = plantId + "::" + variableId
        if variable in librariesNames:
            librariesNames[variable]["ids"].append(library["id"])
        else:
            librariesNames[variable] = {"variable":variable, "ids": [library["id"]]}
       
    return json.dumps({"libraries": librariesNames.values()})

#Returns the library information associated to a given variable
@app.route("/getlibrary", methods=["POST", "GET"])
def getlibrary():
    db = getDB()
    tableLibraries = db["libraries"]
    libJson = {}
    if (request.method == "GET"):
        requestedVariable = request.args["variable"].split("::")
        plantId = requestedVariable[0]  
        variableId = requestedVariable[1]  
        requestedLibraryName = request.args["libraryName"]
        libraryDB = tableLibraries.find_one(plant_id=plantId, variable_id=requestedVariable, id=requestedLibraryName)
        libJson["value"] = pickle.loads(libraryDB["value"]),
        libJson["owner"] = libraryDB["user_id"],
        libJson["description"] = libraryDB["description"] 
    return json.dumps(libJson)

#Updates the library information associated to a given variable
@app.route("/savelibrary", methods=["POST", "GET"])
def savelibrary():
    db = getDB()
    tableLibraries = db["libraries"]
    if (request.method == "GET"):
        requestedVariable = request.args["variable"].split("::")
        plantId = requestedVariable[0]  
        variableId = requestedVariable[1]  
        requestedLibraryName = request.args["libraryName"]
        requestedLibraryDescription = request.args["libraryDescription"]
        requestedLibraryValues = request.args["libraryValues"]
        lib = {
            "plant_id": plantId,
            "variable_id": variableId, 
            "id": requestedLibraryName,
            "description": requestedLibraryDescription,
            "user_id": "codac-dev-1",
            "value": pickle.dumps(json.loads(requestedLibraryValues))
        }

        #Check if the library already exists (and in the future prevent it from being overwritten if was ever used)
        tableLibraries.upsert(lib, ["id", "variable_id", "plant_id"]);    
    return "ok" 



#Returns the variables associated to a given schedule
@app.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    variables = []
    db = getDB()
    #TODO missing plant id...
    scheduleVariablesTable = db["schedule_variables"]
    if (request.method == "GET"):
        requestedSchedule = request.args["schselect"]
        scheduleVariables = scheduleVariablesTable.find(schedule_id=requestedSchedule)
        for v in scheduleVariables:
            vp = {
                "variableId": v["variable_id"],
                "plantId": v["plant_id"],
                "value": pickle.loads(v["value"])
            } 
            variables.append(vp)
    return json.dumps(variables)


@app.route("/stream")
def stream():
    return Response(streamData(), mimetype="text/event-stream")

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)

if __name__ == "__main__":
    epics.ca.find_libca()
    
    parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Server port")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    args = parser.parse_args()

    db = getDB()
    plantVariables = db["plant_variables"]
    for plantVariable in plantVariables:
        if ("value" not in plantVariable) or (plantVariable["value"] == None):
            plantVariable["value"] = plantVariable["initialValue"]
            plantVariables.upsert(plantVariable, ["id"])

        if plantVariable["epicsPV"] == 1:
            pvName = plantVariable["plant_id"] + "::" + plantVariable["id"]
            camonitor(pvName, None, pvValueChanged)

    app.debug = True
    app.run(threaded= True, host=args.host, port=args.port)
