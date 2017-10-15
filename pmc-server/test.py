import argparse
import Queue
import threading
import epics
from epics import caget, caput, camonitor
import time
import json
import uuid
from flask import Flask, Response, request, send_from_directory

#Only log errors
import logging
log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

#Manage easy integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

#The web app which is a Flask standard application
app = Flask(__name__, static_url_path="")

#Synchronised queue between the SSE stream_data and stream_schedule_data functions. One queue per consumer thread. Should be further protected with semaphores
threadPlantQueues = {}
threadScheduleQueues = {}

#Maximum time that a user is allowed to be logged in without interacting with the database
LOGIN_TIMEOUT = 3600

#Cleans the threadDBs, threadPlantQueues and threadScheduleQueues 
alive = True
def threadCleaner():
    db = getDB()
    while alive:
        time.sleep(5)
        for t in allThreads:
            if (not t.isAlive()):
                tid = str(t)
                allThreads.remove(t)
                #Do not delete the MainThread!
                if ("MainThread" not in tid):
                    threadDBs.pop(tid, None)
                    threadPlantQueues.pop(tid, None)
                    threadScheduleQueues.pop(tid, None)
        #Clean all the users that have not interacted with the server for a while
        currentTime = int(time.time())
        db.query("DELETE FROM logins WHERE '(" + str(currentTime) + " - last_interaction_time) > " + str(LOGIN_TIMEOUT) + "'");
       
def isTokenValid(request):
    ok = ("token" in request.form)
    if (ok): 
        db = getDB()
        loginsTable = db["logins"]
        row = loginsTable.find_one(token_id=request.form["token"])
        ok = (row is not None)
    return ok

#A DB access cannot be shared between different threads.
#This function allocates a DB instance for any given thread
threadDBs = {}
allThreads = []
def getDB():
    ct = threading.current_thread()
    tid = str(ct)
    if tid not in threadDBs:
        threadDBs[tid] = dataset.connect('sqlite:////tmp/pmc-server.db')
        if (ct not in allThreads):
            allThreads.append(ct)
    return threadDBs[tid]
    

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadPlantQueues.iteritems():
        pvname = pvname.split("::")
        plantId = pvname[0]
        variableId = pvname[1]
        q.put((plantId, variableId, value), True)

def updatePlantVariablesDB(plantId, variableId, variableValue):
    db = getDB()
    plantVariables = db["plant_variables"]
    row = plantVariables.find_one(id=variableId,plant_id=plantId)
    if (row is not None):
        row["value"] = pickle.dumps(variableValue);
        plantVariables.upsert(row, ["id", "plant_id"])

def updateScheduleVariablesDB(plantId, variableId, scheduleId, variableValue):
    db = getDB()
    scheduleVariables = db["schedule_variables"]
    row = {
        "variable_id": variableId,
        "plant_id": plantId,
        "schedule_id": scheduleId,
        "value": pickle.dumps(variableValue)
    }
    scheduleVariables.upsert(row, ["variable_id", "plant_id", "schedule_id"])

#Streams plant data changes
#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamPlantData():
    try:
        while True:
            db = getDB()
            ct = threading.current_thread()
            tid = str(ct)
            plantVariables = db["plant_variables"]
            if tid not in threadPlantQueues:
                # The first time send all the variables
                threadPlantQueues[tid] = Queue.Queue()
                if (ct not in allThreads):
                    allThreads.append(ct)
                encodedPy = {"plantVariables": [ ] }
                for plantVariable in plantVariables:
                    variableId = plantVariable["id"]
                    plantId = plantVariable["plant_id"]
                    value = pickle.loads(plantVariable["value"])
                    encodedPy["plantVariables"].append({"variableId" : variableId, "plantId" : plantId, "value" : value})
                encodedJson = json.dumps(encodedPy)
            else:
                # Just monitor on change 
                monitorQueue = threadPlantQueues[tid]
                updatedPV = monitorQueue.get(True)
                plantId = updatedPV[0]
                variableId = updatedPV[1]
                value = updatedPV[2]
                encodedPy = {"plantVariables": [ {"variableId" : variableId, "plantId" : plantId, "value" : value}] }
                encodedJson = json.dumps(encodedPy)
                monitorQueue.task_done()
            yield "data: {0}\n\n".format(encodedJson)
    except Exception as e:
        print "Exception ignored"
        print e
        #ignore

def streamScheduleData():
    try:
        while True:
            db = getDB()
            ct = threading.current_thread()
            tid = str(ct)
            scheduleVariables = db["schedule_variables"]
            if tid not in threadScheduleQueues:
                # The first time just register the Queue 
                threadScheduleQueues[tid] = Queue.Queue()
                if (ct not in allThreads):
                    allThreads.append(ct)
            # Monitor on change 
            monitorQueue = threadScheduleQueues[tid]
            updatedPV = monitorQueue.get(True)
            plantId = updatedPV[0]
            variableId = updatedPV[1]
            scheduleId = updatedPV[2]
            value = updatedPV[3]
            encodedPy = {"scheduleVariables": [ {"variableId" : variableId, "plantId" : plantId, "scheduleId": scheduleId, "value" : value}] }
            encodedJson = json.dumps(encodedPy)
            monitorQueue.task_done()
            yield "data: {0}\n\n".format(encodedJson)
    except Exception as e:
        print "Exception ignored"
        print e
        #ignore


#Gets all the pv information
@app.route("/getplantinfo", methods=["POST", "GET"])
def getplantinfo():
    db = getDB()
    plantVariables = db["plant_variables"]
    validations = db["validations"]
    permissions = db["permissions"]
    toReturn = ""
   
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    elif ("variables" not in request.form):
        toReturn = "InvalidParameters"
    else: 
        requestedVariables = request.form["variables"]
        jSonRequestedVariables = json.loads(requestedVariables)
        encodedPy = {"variables": [] }
        for requestedVariable in jSonRequestedVariables:
            varName = requestedVariable.split("::")
            if (len(varName) == 2):
                plantId = varName[0]
                variableId = varName[1]
                plantVariable = plantVariables.find_one(plant_id=plantId, id=variableId)
                if (plantVariable is not None):
                    plantVariable["variableId"] = plantVariable["id"]  
                    plantVariable["plantId"] = plantVariable["plant_id"]  
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

                    plantVariable["permissions"] = []
                    permission = permissions.find(plant_id=plantVariable["plant_id"], variable_id=plantVariable["id"])
                    for p in permission:
                        plantVariable["permissions"].append(p["group_id"])
                    
                    encodedPy["variables"].append(plantVariable) 
        

        toReturn = json.dumps(encodedPy)
    return toReturn 
  
#Try to update the values in the plant
@app.route("/submit", methods=["POST", "GET"])
def submit():
    toReturn = "done"
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    elif ("update" not in request.form):
        toReturn = "InvalidParameters"
    else: 
        updateJSon = request.form["update"]
        jSonUpdateVariables = json.loads(updateJSon)
        for varName in jSonUpdateVariables.keys():
            newValue = jSonUpdateVariables[varName]
            varName = varName.split("::")
            if len(varName) == 2:
                plantId = varName[0]
                variableId = varName[1]
                updatePlantVariablesDB(plantId, variableId, newValue)
                #Warn others that the plant values have changed!
                for k, q in threadPlantQueues.iteritems():
                    q.put((plantId, variableId, newValue), True)

            #caput(k, request.args[k])
    return toReturn

#Return the available schedules
@app.route("/getschedules", methods=["POST", "GET"])
def getschedules():
    db = getDB()
    userId = ""
    schedules = []
    toReturn = "done"
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        if "userId" in request.form:
            userId = request.form["userId"]
        tableSchedules = db["schedules"]
        if (len(userId) == 0):
            for s in tableSchedules:
                schedules.append(s);
        else:
            schedulesUser = tableSchedules.find(user_id=userId)
            for s in schedulesUser:
                schedules.append(s);
        toReturn = json.dumps(schedules)
    return toReturn

#Returns the variables associated to a given schedule
@app.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    toReturn = ""
    variables = []
    db = getDB()
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else: 
        scheduleVariablesTable = db["schedule_variables"]
        requestedSchedule = request.form["schselect"]
        scheduleVariables = scheduleVariablesTable.find(schedule_id=requestedSchedule)
        for v in scheduleVariables:
            vp = {
                "variableId": v["variable_id"],
                "plantId": v["plant_id"],
                "value": pickle.loads(v["value"])
            } 
            variables.append(vp)
        toReturn = json.dumps(variables)
    return toReturn

#Return the available libraries
@app.route("/getlibraries", methods=["POST", "GET"])
def getlibraries():
    db = getDB()
    tableLibraries = db["libraries"]
    librariesNames = {}
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else: 
        for library in tableLibraries:
            plantId = library["plant_id"]
            variableId = library["variable_id"]
            variable = plantId + "::" + variableId
            if variable in librariesNames:
                librariesNames[variable]["ids"].append(library["id"])
            else:
                librariesNames[variable] = {"variable":variable, "ids": [library["id"]]}
        toReturn = json.dumps({"libraries": librariesNames.values()}) 
    return toReturn

#Returns the library information associated to a given variable
@app.route("/getlibrary", methods=["POST", "GET"])
def getlibrary():
    db = getDB()
    tableLibraries = db["libraries"]
    libJson = {}
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        requestedVariable = request.form["variable"].split("::")
        plantId = requestedVariable[0]  
        variableId = requestedVariable[1]  
        requestedLibraryName = request.form["libraryName"]
        libraryDB = tableLibraries.find_one(plant_id=plantId, variable_id=requestedVariable, id=requestedLibraryName)
        libJson["value"] = pickle.loads(libraryDB["value"]),
        libJson["owner"] = libraryDB["user_id"],
        libJson["description"] = libraryDB["description"] 
        toReturn = json.dumps(libJson)
    return toReturn

#Updates the library information associated to a given variable
@app.route("/savelibrary", methods=["POST", "GET"])
def savelibrary():
    db = getDB()
    tableLibraries = db["libraries"]
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        requestedVariable = request.form["variable"].split("::")
        plantId = requestedVariable[0]  
        variableId = requestedVariable[1]  
        requestedLibraryName = request.form["libraryName"]
        requestedLibraryDescription = request.form["libraryDescription"]
        requestedLibraryValues = request.form["libraryValues"]
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
        toReturn = "ok"
    return toReturn

#Tries to login the current user
@app.route("/login", methods=["POST", "GET"])
def login():
    db = getDB()
    usersTable = db["users"]
    groupMembersTable = db["group_members"]
    user = {}
    requestedUserId = request.form["userId"]
    user = usersTable.find_one(id=requestedUserId)
    if (user is not None): 
        user["password"] = ""
        user["token"] = "" + uuid.uuid4().hex
        user["groups"] = []
        groups = groupMembersTable.find(user_id=requestedUserId)
        for group in groups:
            user["groups"].append(group["group_id"])

        loginsTable = db["logins"]
        login = {
            "token_id": user["token"],
            "user_id": user["id"],
            "last_interaction_time": int(time.time())
        }
        loginsTable.insert(login)
    else:
        user = {
            "id": ""
        }
    return json.dumps(user)

#Updates a schedule variable
@app.route("/updateschedule", methods=["POST", "GET"])
def updateschedule():
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        updateJSon = request.form["update"]
        jSonUpdateSchedule = json.loads(updateJSon)
        scheduleId = jSonUpdateSchedule["scheduleId"]
        values = jSonUpdateSchedule["values"]
        for v in values:
            varName = v["id"].split("::")
            if (len(varName) == 2):
                plantId = varName[0]
                variableId = varName[1]
                value = v["value"]
                updateScheduleVariablesDB(plantId, variableId, scheduleId, value)
                #Warn (only the!) others that the scheduler values have changed!
                for k, q in threadScheduleQueues.iteritems():
                    tid = str(threading.current_thread())
                    if (k != tid):
                        q.put((plantId, variableId, scheduleId, value), True)
        toReturn = "ok"
    return toReturn

#Creates a new schedule
@app.route("/createschedule", methods=["POST", "GET"])
def createschedule():
    db = getDB()
    schedulesTable = db["schedules"]
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        schedule = {
            "id": request.form["name"],
            "name": request.form["name"],
            "description": request.form["description"],
            "user_id": request.form["userId"],
        }
        schedulesTable.insert(schedule);    

        if ("sourceSchedule" in request.form):
            db.query("INSERT INTO schedule_variables(variable_id, plant_id, schedule_id, user_id, value) SELECT schedule_variables.variable_id, schedule_variables.plant_id, '" + schedule["id"] + "', '" + schedule["user_id"] + "', schedule_variables.value FROM schedule_variables WHERE schedule_variables.schedule_id='" + request.form["sourceSchedule"] + "'")
        else:
            db.begin()
            jSonRequestedVariables = json.loads(request.form["plantVariables"])
            for requestedVariable in jSonRequestedVariables:
                varName = requestedVariable.split("::")
                if (len(varName) == 2):
                    plantId = varName[0]
                    variableId = varName[1]
                    db.query("INSERT INTO schedule_variables(variable_id, plant_id, schedule_id, user_id, value) SELECT '" + variableId + "','" + plantId + "','" + schedule["id"] + "', '" + schedule["user_id"] + "', plant_variables.value FROM plant_variables WHERE id='" + variableId + "' AND plant_id='" + plantId + "'")
            db.commit()
            
        toReturn = "ok"
    return toReturn


@app.route("/streamplant")
def streamplant():
    return Response(streamPlantData(), mimetype="text/event-stream")

@app.route("/streamschedule")
def streamschedule():
    return Response(streamScheduleData(), mimetype="text/event-stream")


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
        db.begin()
        if ("value" not in plantVariable) or (plantVariable["value"] == None):
            plantVariable["value"] = plantVariable["initialValue"]
            plantVariables.upsert(plantVariable, ["id", "plant_id"])
        db.commit()

        if plantVariable["epicsPV"] == 1:
            pvName = plantVariable["plant_id"] + "::" + plantVariable["id"]
            camonitor(pvName, None, pvValueChanged)

    #Clean dead threads
    t = threading.Thread(target=threadCleaner)
    #To force the killing of the threadCleaner thread with Ctrl+C
    t.daemon = True
    t.start()


    app.debug = True
    #Running a threaded Flask is ok only for debugging
    app.run(threaded=True, host=args.host, port=args.port)

    alive = False
