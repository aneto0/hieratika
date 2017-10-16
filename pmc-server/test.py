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
        q.put((pvName, value), True)

def updatePlantVariablesDB(variableId, variableValue):
    db = getDB()
    variables = db["variables"]
    row = variables.find_one(id=variableId)
    if (row is not None):
        row["value"] = pickle.dumps(variableValue);
        variables.upsert(row, ["id"])

def updateScheduleVariablesDB(variableId, scheduleId, variableValue):
    db = getDB()
    scheduleVariables = db["schedule_variables"]
    row = {
        "variable_id": variableId,
        "schedule_id": scheduleId,
        "value": pickle.dumps(variableValue)
    }
    scheduleVariables.upsert(row, ["variable_id", "schedule_id"])

#Streams plant data changes
#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamPlantData():
    try:
        while True:
            db = getDB()
            ct = threading.current_thread()
            tid = str(ct)
            variables = db["variables"]
            if tid not in threadPlantQueues:
                # The first time send all the variables
                threadPlantQueues[tid] = Queue.Queue()
                if (ct not in allThreads):
                    allThreads.append(ct)
                encodedPy = {"variables": [ ] }
                for variable in variables:
                    variableId = variable["id"]
                    value = pickle.loads(variable["value"])
                    encodedPy["variables"].append({"variableId" : variableId, "value" : value})
                encodedJson = json.dumps(encodedPy)
            else:
                # Just monitor on change 
                monitorQueue = threadPlantQueues[tid]
                updatedPV = monitorQueue.get(True)
                variableId = updatedPV[0]
                value = updatedPV[1]
                encodedPy = {"variables": [ {"variableId" : variableId, "value" : value}] }
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
            variableId = updatedPV[0]
            scheduleId = updatedPV[1]
            value = updatedPV[2]
            encodedPy = {"scheduleVariables": [ {"variableId" : variableId, "scheduleId": scheduleId, "value" : value}] }
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
    variables = db["variables"]
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
        for variableId in jSonRequestedVariables:
            variable = variables.find_one(id=variableId)
            if (variable is not None):
                variable["variableId"] = variable["id"]  
                variable["library"] = (variable["library"] == 1)
                variable["initialValue"] = pickle.loads(variable["initialValue"])  
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
                
                encodedPy["variables"].append(variable) 
        

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
        for variableId in jSonUpdateVariables.keys():
            newValue = jSonUpdateVariables[variableId]
            updatePlantVariablesDB(variableId, newValue)
            #Warn others that the plant values have changed!
            for k, q in threadPlantQueues.iteritems():
                q.put((variableId, newValue), True)

            #caput(k, request.args[k])
    return toReturn

#Return the available schedules
@app.route("/getschedules", methods=["POST", "GET"])
def getschedules():
    db = getDB()
    userId = ""
    schedules = []
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        pageId = request.form["pageId"]
        if "userId" in request.form:
            userId = request.form["userId"]

        tableSchedules = db["schedules"]
        if (len(userId) == 0):
            schedulesAllUsers = tableSchedules.find(page_id=pageId)
            for s in schedulesAllUsers:
                schedules.append(s);
        else:
            schedulesUser = tableSchedules.find(page_id=pageId, user_id=userId)
            for s in schedulesUser:
                schedules.append(s);
        toReturn = json.dumps(schedules)
    return toReturn

#Return the available pages
@app.route("/getpages", methods=["POST", "GET"])
def getpages():
    db = getDB()
    userId = ""
    pages = []
    toReturn = ""
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else:
        tablePages = db["pages"]
        for p in tablePages:
            pages.append(p);
        toReturn = json.dumps(pages)
    return toReturn

#Returns the properties of a given page 
@app.route("/getpage", methods=["POST", "GET"])
def getpage():
    toReturn = ""
    variables = []
    db = getDB()
    if (not isTokenValid(request)):
        toReturn = "InvalidToken"
    else: 
        pageId = request.form["pageId"]
        pages = db["pages"]
        page = pages.find_one(id=pageId)
        toReturn = json.dumps(page)
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
        pmcLibVariables = json.loads(request.form["variables"])
        for variable in pmcLibVariables:
            libraries = tableLibraries.find(variable_id=variable)
            for library in libraries:
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
        variableId = request.form["variable"]
        requestedLibraryName = request.form["libraryName"]
        libraryDB = tableLibraries.find_one(variable_id=variableId, id=requestedLibraryName)
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
        variableId = request.form["variable"]
        requestedLibraryName = request.form["libraryName"]
        requestedLibraryDescription = request.form["libraryDescription"]
        requestedLibraryValues = request.form["libraryValues"]
        lib = {
            "variable_id": variableId, 
            "id": requestedLibraryName,
            "description": requestedLibraryDescription,
            "user_id": "codac-dev-1",
            "value": pickle.dumps(json.loads(requestedLibraryValues))
        }

        #Check if the library already exists (and in the future prevent it from being overwritten if was ever used)
        tableLibraries.upsert(lib, ["id", "variable_id"]);    
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
            variableId = v["id"]
            value = v["value"]
            updateScheduleVariablesDB(variableId, scheduleId, value)
            #Warn (only the!) others that the scheduler values have changed!
            for k, q in threadScheduleQueues.iteritems():
                tid = str(threading.current_thread())
                if (k != tid):
                    q.put((variableId, scheduleId, value), True)
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
            "page_id": request.form["pageId"]
        }
        schedulesTable.insert(schedule);    

        if ("sourceSchedule" in request.form):
            db.query("INSERT INTO schedule_variables(variable_id, schedule_id, user_id, value) SELECT schedule_variables.variable_id, '" + schedule["id"] + "', '" + schedule["user_id"] + "', schedule_variables.value FROM schedule_variables WHERE schedule_variables.schedule_id='" + request.form["sourceSchedule"] + "'")
        else:
            db.begin()
            jSonRequestedVariables = json.loads(request.form["variables"])
            for variableId in jSonRequestedVariables:
                db.query("INSERT INTO schedule_variables(variable_id, schedule_id, user_id, value) SELECT '" + variableId + "','" + schedule["id"] + "', '" + schedule["user_id"] + "', variables.value FROM variables WHERE id='" + variableId + "'")
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
    variables = db["variables"]
    for variable in variables:
        db.begin()
        if ("value" not in variable) or (variable["value"] == None):
            variable["value"] = variable["initialValue"]
            variables.upsert(variable, ["id"])
        db.commit()

        if variable["epicsPV"] == 1:
            pvName = variable["id"]
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
