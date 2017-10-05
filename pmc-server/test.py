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
    

def createDB():
    #Assume that only one plant exists for the time being
    db = getDB()
    tablePlantDescription = db["PMC::TEST::PLANT1"]
    tablePlantValidations = db["PMC::TEST::PLANT1-validations"]
    if not tablePlantDescription.exists:
        with open("plant-variables.json") as jsonFile:
            plantVariablesDBJSon = json.load(jsonFile)
 
        #Assume the first plant for the time being
        plantVariablesDB = plantVariablesDBJSon["plants"][0]["variables"]
        tablePlantDescription = db.create_table("PMC::TEST::PLANT1", primary_id="name", primary_type=db.types.text)
        tablePlantValidations = db.create_table("PMC::TEST::PLANT1-validations")
        for plantVariable in plantVariablesDB:
            #Serialize the arrays
            plantVariable["initialValue"] = pickle.dumps(plantVariable["initialValue"])  
            plantVariable["numberOfElements"] = pickle.dumps(plantVariable["numberOfElements"])  
            if "validation" in plantVariable:
                for v in plantVariable["validation"]:
                    vp = {
                        "plantVariable": str(plantVariable["name"]),
                        "description": v["description"],
                        "fun": v["fun"],
                        "parameters": pickle.dumps(v["parameters"])  
                    }
                    tablePlantValidations.insert(vp)
                plantVariable.pop("validation")
            tablePlantDescription.insert(plantVariable)

    tableSchedules = db["PMC::TEST::PLANT1-schedules"]
    if not tableSchedules.exists:
        tableSchedules = db.create_table("PMC::TEST::PLANT1-schedules", primary_id="name", primary_type=db.types.text)
        tableSchedulesVariables = db.create_table("PMC::TEST::PLANT1-schedules-variables")
        with open("static/schedules.json") as jsonFile:
            schedulesJson = json.load(jsonFile)
            schedules = schedulesJson["schedules"]
            for schedule in schedules:
                if "variables" in schedule:
                    for v in schedule["variables"]:
                        vp = {
                            "schedule": schedule["name"],
                            "name": v["name"],
                            "value": pickle.dumps(v["value"])
                        }
                        tableSchedulesVariables.insert(vp)
                    schedule.pop("variables")
                tableSchedules.insert(schedule);

    tableLibraries = db["PMC::TEST::PLANT1-libraries"]
    if not tableLibraries.exists:
        tableLibraries = db.create_table("PMC::TEST::PLANT1-libraries")
        with open("static/libraries.json") as jsonFile:
            librariesJson = json.load(jsonFile)
            librariesVariables = librariesJson["libraries"]
            for libraryVariable in librariesVariables:
                variable = libraryVariable["variable"]
                for library in libraryVariable["libraries"]:
                    lib = {
                        "variable": variable, 
                        "name": library["name"],
                        "owner": library["owner"],
                        "description": library["description"],
                        "values": pickle.dumps(library["values"])
                    }
                    tableLibraries.insert(lib)

#Synchronised queue between the SSE stream_data function and the pvValueChanged. One queue per consumer thread. Should be further protected with semaphores
#TODO this will have to be cleared from time to time
threadQueues = {}

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadQueues.iteritems():
        q.put((pvname, value), True)

def updatePlantVariablesDB(pvName, pvValue):
    tablePlantDescription = getDB()["PMC::TEST::PLANT1"]
    row = tablePlantDescription.find_one(name=pvName)
    if (row is not None):
        row["value"] = pickle.dumps(pvValue);
        tablePlantDescription.upsert(row, ["name"])

#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamData():
    try:
        while True:
            db = getDB()
            tid = str(threading.current_thread())
            tablePlantDescription = db["PMC::TEST::PLANT1"]
            if tid not in threadQueues:
                # The first time send all the variables
                threadQueues[tid] = Queue.Queue()
                encodedPy = {"plantVariables": [ ] }
                for plantVariable in tablePlantDescription:
                    pvName = plantVariable["name"]
                    value = pickle.loads(plantVariable["value"])
                    encodedPy["plantVariables"].append({"name" : pvName, "value" : value})
                encodedJson = json.dumps(encodedPy)
            else:
                # Just monitor on change 
                monitorQueue = threadQueues[tid]
                updatedPV = monitorQueue.get(True)
                pvName = updatedPV[0]
                pvValue = updatedPV[1]
                encodedPy = {"plantVariables": [ {"name" : pvName, "value" : pvValue}] }
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
    tablePlantDescription = db["PMC::TEST::PLANT1"]
    tablePlantValidations = db["PMC::TEST::PLANT1-validations"]
    encodedPy = {"variables": [] }
    for plantVariable in tablePlantDescription:
        plantVariable["initialValue"] = pickle.loads(plantVariable["initialValue"])  
        plantVariable["value"] = pickle.loads(plantVariable["value"])  
        plantVariable["numberOfElements"] = pickle.loads(plantVariable["numberOfElements"])  
        plantVariable["validation"] = []  
        validation = tablePlantValidations.find(plantVariable=plantVariable["name"])
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
            updatePlantVariablesDB(varName, newValue)
            #Warn others that the plant values have changed!
            for k, q in threadQueues.iteritems():
                q.put((varName, newValue), True)

            #caput(k, request.args[k])
    return "done"

#Return the available schedules
@app.route("/getschedules")
def getschedules():
    db = getDB()
    tableSchedules = db["PMC::TEST::PLANT1-schedules"]
    scheduleNames = []
    for s in tableSchedules:
        scheduleNames.append(s["name"]);
    return json.dumps(scheduleNames)

#Return the available libraries
@app.route("/getlibraries")
def getlibraries():
    db = getDB()
    tableLibraries = db["PMC::TEST::PLANT1-libraries"]
    librariesNames = {}
    for library in tableLibraries:
        variable = library["variable"]
        if variable in librariesNames:
            librariesNames[variable]["names"].append(library["name"])
        else:
            librariesNames[variable] = {"variable":variable, "names": [library["name"]]}
       
    return json.dumps({"libraries": librariesNames.values()})

#Returns the library information associated to a given variable
@app.route("/getlibrary", methods=["POST", "GET"])
def getlibrary():
    db = getDB()
    tableLibraries = db["PMC::TEST::PLANT1-libraries"]
    libJson = {}
    if (request.method == "GET"):
        requestedVariable = request.args["variable"]
        requestedLibraryName = request.args["libraryName"]
        libraryDB = tableLibraries.find_one(variable=requestedVariable, name=requestedLibraryName)
        libJson["values"] = pickle.loads(libraryDB["values"]),
        libJson["owner"] = libraryDB["owner"],
        libJson["description"] = libraryDB["description"] 
    return json.dumps(libJson)

#Updates the library information associated to a given variable
@app.route("/savelibrary", methods=["POST", "GET"])
def savelibrary():
    db = getDB()
    tableLibraries = db["PMC::TEST::PLANT1-libraries"]
    if (request.method == "GET"):
        requestedVariable = request.args["variable"]
        requestedLibraryName = request.args["libraryName"]
        requestedLibraryDescription = request.args["libraryDescription"]
        requestedLibraryValues = request.args["libraryValues"]
        lib = {
            "variable": requestedVariable, 
            "name": requestedLibraryName,
            "owner": "TODO",
            "values": pickle.dumps(json.loads(requestedLibraryValues))
        }

        #Check if the library already exists (and in the future prevent it from being overwritten if was ever used)
        tableLibraries.upsert(lib, ["variable", "name"]);    
    return "ok" 



#Returns the variables associated to a given schedule
@app.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    variables = []
    db = getDB()
    tableSchedulesVariables = db["PMC::TEST::PLANT1-schedules-variables"]
    if (request.method == "GET"):
        requestedSchedule = request.args["schselect"]
        scheduleVariables = tableSchedulesVariables.find(schedule=requestedSchedule)
        for v in scheduleVariables:
            vp = {
                "name": v["name"],
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

      
    createDB(); 

    db = getDB()
    tablePlantDescription = db["PMC::TEST::PLANT1"]
    for plantVariable in tablePlantDescription:
        if "value" not in plantVariable:
            plantVariable["value"] = plantVariable["initialValue"]
            tablePlantDescription.upsert(plantVariable, ["name"])

        if plantVariable["epicsPV"] == "true":
            camonitor(plantVariable["name"], None, pvValueChanged)

    app.debug = True
    app.run(threaded= True, host=args.host, port=args.port)
