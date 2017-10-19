import argparse
import threading
from multiprocessing import Process
import os
import epics
from epics import caget, caput, camonitor
import time
import json
import uuid
from flask import Flask, Response, request, send_from_directory
from socket import *

#Only log errors
import logging
log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

#Manage easy integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

#Maximum time that a user is allowed to be logged in without interacting with the database
LOGIN_TIMEOUT = 3600
UDP_BROADCAST_PLANT_PORT = 23450
UDP_BROADCAST_SCHEDULE_PORT = 23451

class Server:
    #A DB access cannot be shared between different threads.
    #This function allocates a DB instance for any given thread
    threadDBs = {}
    allThreads = []

    #The web app which is a Flask standard application
    app = Flask(__name__, static_url_path="")
    alive = True

    #Synchronised queue between the SSE stream_data and stream_schedule_data functions. One queue per consumer thread. Should be further protected with semaphores
    threadPlantQueues = {}
    threadScheduleQueues = {}

    #IPC using UDP sockets
    udpPlantBroadcastClient = socket(AF_INET, SOCK_DGRAM)
    udpScheduleBroadcastClient = socket(AF_INET, SOCK_DGRAM)
    udpPlantBroadcastServer = socket(AF_INET, SOCK_DGRAM)
    udpPlantBroadcastServer.settimeout(10)
    udpScheduleBroadcastServer = socket(AF_INET, SOCK_DGRAM)
    udpScheduleBroadcastServer.settimeout(10)

    def __init__(self):
        epics.ca.find_libca()
        db = self.getDB()
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

        self.udpPlantBroadcastClient.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udpPlantBroadcastClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udpScheduleBroadcastClient.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udpScheduleBroadcastClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udpPlantBroadcastServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udpPlantBroadcastServer.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udpScheduleBroadcastServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udpScheduleBroadcastServer.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.udpPlantBroadcastServer.bind(("127.255.255.0", UDP_BROADCAST_PLANT_PORT))
        self.udpScheduleBroadcastServer.bind(("127.255.255.0", UDP_BROADCAST_SCHEDULE_PORT))

        #Clean dead threads
        self.monitorThread = threading.Thread(target=self.threadCleaner)

    def start(self):
        #To force the killing of the threadCleaner thread with Ctrl+C
        self.monitorThread.daemon = True
        self.monitorThread.start()

        self.app.debug = True
        #Running a threaded Flask is ok only for debugging
        #app.run(threaded=False, host=args.host, port=args.port)
        self.app.run(host='0.0.0.0')
        self.alive = False

    def getDB(self):
        ct = threading.current_thread()
        tid = str(ct)
        if tid not in self.threadDBs:
            self.threadDBs[tid] = dataset.connect('sqlite:////tmp/pmc-server.db')
            if (ct not in self.allThreads):
                self.allThreads.append(ct)
        return self.threadDBs[tid]

    #Cleans the threadDBs, threadPlantQueues and threadScheduleQueues 
    def threadCleaner(self):
        db = self.getDB()
        while self.alive:
            time.sleep(5)
            for t in self.allThreads:
                if (not t.isAlive()):
                    tid = str(t)
                    self.allThreads.remove(t)
                    #Do not delete the MainThread!
                    if ("MainThread" not in tid):
                        self.threadDBs.pop(tid, None)
                        self.threadPlantQueues.pop(tid, None)
                        self.threadScheduleQueues.pop(tid, None)
            #Clean all the users that have not interacted with the server for a while
            currentTime = int(time.time())
            db.query("DELETE FROM logins WHERE '(" + str(currentTime) + " - last_interaction_time) > " + str(LOGIN_TIMEOUT) + "'");
       
    def isTokenValid(self, request):
        if (request.method == "POST"):
            ok = ("token" in request.form)
            if (ok):
                tokenId = request.form["token"]
        else:
            ok = ("token" in request.args)
            if (ok):
                tokenId = request.args["token"]
        if (ok): 
            db = self.getDB()
            loginsTable = db["logins"]
            row = loginsTable.find_one(token_id=tokenId)
            ok = (row is not None)
        return ok

    #see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
    def pvValueChanged(self, pvname=None, value=None, **kw):
        for k, q in self.threadPlantQueues.iteritems():
            q.put((pvName, value), True)

    def updatePlantVariablesDB(self, variableId, variableValue):
        db = self.getDB()
        variables = db["variables"]
        row = variables.find_one(id=variableId)
        if (row is not None):
            row["value"] = pickle.dumps(variableValue);
            variables.upsert(row, ["id"])

    def updateScheduleVariablesDB(self, variableId, scheduleId, variableValue):
        db = self.getDB()
        scheduleVariables = db["schedule_variables"]
        row = {
            "variable_id": variableId,
            "schedule_id": scheduleId,
            "value": pickle.dumps(variableValue)
        }
        scheduleVariables.upsert(row, ["variable_id", "schedule_id"])

    #Streams plant data changes
    #Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
    def streamPlantData(self):
        firstTime = True
        try:
            while True:
                ct = threading.current_thread() 
                tid = str(os.getpid()) + "-" + str(ct)
                #if tid not in self.threadPlantQueues:
                if (firstTime):
                    # The first time send all the variables
                    #self.threadPlantQueues[tid] = Queue()
                    if (ct not in self.allThreads):
                        self.allThreads.append(ct)
                    encodedPy = {"variables": [ ] }
                    db = self.getDB()
                    variables = db["variables"]
                    for variable in variables:
                        variableId = variable["id"]
                        value = pickle.loads(variable["value"])
                        encodedPy["variables"].append({"variableId" : variableId, "value" : value})
                    encodedJson = json.dumps(encodedPy)
                    firstTime = False
                else:
                    # Just monitor on change 
                    #monitorQueue = self.threadPlantQueues[tid]
                    try:
                    #    updatedPV = monitorQueue.get(True, 1)
                    #    variableId = updatedPV[0]
                    #    value = updatedPV[1]
                    #    encodedPy = {"variables": [ {"variableId" : variableId, "value" : value}] }
                    #    encodedJson = json.dumps(encodedPy)
                    #    monitorQueue.task_done()
                        print "GO"
                        encodedJson = self.udpPlantBroadcastServer.recvfrom(4096)
                    except timeout:
                    #except Empty:
                        time.sleep(0.01)
                        encodedJson = "" 
                    print encodedJson
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            print "Exception ignored"
            print e
            #ignore

    def streamScheduleData(self):
        firstTime = True
        try:
            while True:
                ct = threading.current_thread()
                tid = str(os.getpid()) + "-" + str(ct)
                #if tid not in self.threadScheduleQueues:
                if (firstTime):
                    # The first time just register the Queue and send back the TID so that updates from this client are not sent back to itself (see updateschedule)
                    #self.threadScheduleQueues[tid] = Queue()
                    if (ct not in self.allThreads):
                        self.allThreads.append(ct)
                    encodedPy = {"tid": tid}
                    encodedJson = json.dumps(encodedPy)
                    firstTime = False
                else:
                    # Monitor on change 
                    #monitorQueue = self.threadScheduleQueues[tid]
                    try:
                    #    updatedPV = monitorQueue.get(True, 1)
                    #    variableId = updatedPV[0]
                    #    scheduleId = updatedPV[1]
                    #    value = updatedPV[2]
                    #    encodedPy = {"scheduleVariables": [ {"variableId" : variableId, "scheduleId": scheduleId, "value" : value}] }
                    #    encodedJson = json.dumps(encodedPy)
                    #    monitorQueue.task_done()
                    #except Empty:
                        print "GO"
                        encodedJson = self.udpScheduleBroadcastServer.recvfrom(4096)
                    except timeout:
                        time.sleep(0.01)
                        encodedJson = "" 
                    print encodedJson
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            print "Exception ignored"
            print e
            #ignore

    def getPlantInfo(self, request):
        db = self.getDB()
        variables = db["variables"]
        validations = db["validations"]
        permissions = db["permissions"]
        toReturn = ""
       
        if (not server.isTokenValid(request)):
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

    def submit(self, request):
        toReturn = "done"
        if (not server.isTokenValid(request)):
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
                #for k, q in threadPlantQueues.iteritems():
                #    jsonToSend = json.dumps("variables": [ {"variableId" : variableId, "value" : newValue}]) 
            self.udpPlantBroadcastClient.sendto(jSonUpdateVariables, ('127.255.255.255', UDP_BROADCAST_PLANT_PORT))

                #caput(k, request.args[k])
        return toReturn

    def getSchedules(self, request):
        db = self.getDB()
        userId = ""
        schedules = []
        toReturn = ""
        if (not server.isTokenValid(request)):
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

    def getUsers(self, request):
        db = self.getDB()
        userId = ""
        users = []
        toReturn = ""
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            allUsers = db["users"]
            for u in allUsers:
                u["password"] = ""
                users.append(u);
            toReturn = json.dumps(users)
        return toReturn

    def getPages(self, request):
        db = self.getDB()
        userId = ""
        pages = []
        toReturn = ""
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            tablePages = db["pages"]
            for p in tablePages:
                pages.append(p);
            toReturn = json.dumps(pages)
        return toReturn

    def getPage(self, request):
        toReturn = ""
        variables = []
        db = self.getDB()
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            pageId = request.form["pageId"]
            pages = db["pages"]
            page = pages.find_one(id=pageId)
            toReturn = json.dumps(page)
        return toReturn

    def getSchedule(self, request):
        toReturn = ""
        db = self.getDB()
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            scheduleId = request.form["scheduleId"]
            schedules = db["schedules"]
            schedule = schedules.find_one(id=scheduleId)
            toReturn = json.dumps(schedule)
        return toReturn

    def getScheduleVariables(self, request):
        toReturn = ""
        variables = []
        db = self.getDB()
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            scheduleVariablesTable = db["schedule_variables"]
            requestedSchedule = request.form["scheduleId"]
            scheduleVariables = scheduleVariablesTable.find(schedule_id=requestedSchedule)
            for v in scheduleVariables:
                vp = {
                    "variableId": v["variable_id"],
                    "value": pickle.loads(v["value"])
                } 
                variables.append(vp)
            toReturn = json.dumps(variables)
        return toReturn

    def getLibraries(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        librariesNames = {}
        toReturn = ""
        if (not server.isTokenValid(request)):
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

    def getLibrary(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        libJson = {}
        toReturn = ""
        if (not server.isTokenValid(request)):
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

    def saveLibrary(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        toReturn = ""
        if (not server.isTokenValid(request)):
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

    def login(self):
        db = self.getDB()
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

    def updateSchedule(self, request):
        toReturn = ""
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            requesterTid = request.form["tid"]
            updateJSon = request.form["update"]
            jSonUpdateSchedule = json.loads(updateJSon)
            scheduleId = jSonUpdateSchedule["scheduleId"]
            values = jSonUpdateSchedule["values"]
            for v in values:
                variableId = v["id"]
                value = v["value"]
                updateScheduleVariablesDB(variableId, scheduleId, value)
                #Warn (only the!) others that the scheduler values have changed!
                #for k, q in threadScheduleQueues.iteritems():
                #    if (k != requesterTid):
                #        q.put((variableId, scheduleId, value), True)
            self.udpScheduleBroadcastClient.sendto(jSonUpdateSchedule, ('127.255.255.255', UDP_BROADCAST_SCHEDULE_PORT))
            
            toReturn = "ok"
        return toReturn

    def createSchedule(self, request):
        db = self.getDB()
        schedulesTable = db["schedules"]
        toReturn = ""
        if (not server.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            schedule = {
                "name": request.form["name"],
                "description": request.form["description"],
                "user_id": request.form["userId"],
                "page_id": request.form["pageId"]
            }
            schedulesTable.insert(schedule)
            createdSchedule = schedulesTable.find_one(user_id=schedule["user_id"], name=schedule["name"], page_id=schedule["page_id"])

            if ("sourceSchedule" in request.form):
                db.query("INSERT INTO schedule_variables(variable_id, schedule_id, value) SELECT schedule_variables.variable_id,'" + str(createdSchedule["id"]) + "', schedule_variables.value FROM schedule_variables WHERE schedule_variables.schedule_id='" + request.form["sourceSchedule"] + "'")
            else:
                db.begin()
                jSonRequestedVariables = json.loads(request.form["variables"])
                for variableId in jSonRequestedVariables:
                    db.query("INSERT INTO schedule_variables(variable_id, schedule_id, value) SELECT '" + variableId + "','" + str(createdSchedule["id"]) + "', variables.value FROM variables WHERE id='" + variableId + "'")
                db.commit()
                
            toReturn = "ok"
        return toReturn

    def info(self):
        print "TODO ADD info (console and http)"

server = Server()
application = server.app

#Gets all the pv information
@application.route("/getplantinfo", methods=["POST", "GET"])
def getplantinfo():
    return server.getPlantInfo(request)
  
#Try to update the values in the plant
@application.route("/submit", methods=["POST", "GET"])
def submit():
    return server.submit(request)
    
#Return the available schedules
@application.route("/getschedules", methods=["POST", "GET"])
def getschedules():
    return server.getSchedules(request) 

#Return the available users
@application.route("/getusers", methods=["POST", "GET"])
def getusers():
    return server.getUsers(request) 

#Return the available pages
@application.route("/getpages", methods=["POST", "GET"])
def getpages():
    return server.getPages(request) 

#Returns the properties of a given page 
@application.route("/getpage", methods=["POST", "GET"])
def getpage():
    return server.getPage(request) 

#Returns the properties of a given schedule
@application.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    return server.getSchedule(request)    

#Returns the variables associated to a given schedule
@application.route("/getschedulevariables", methods=["POST", "GET"])
def getschedulevariables():
    return server.getScheduleVariables(request)

#Return the available libraries
@application.route("/getlibraries", methods=["POST", "GET"])
def getlibraries():
    #Returns the library information associated to a given variable
    return server.getLibraries(request)

@application.route("/getlibrary", methods=["POST", "GET"])
def getlibrary():
    return server.getLibrary(request) 

#Updates the library information associated to a given variable
@application.route("/savelibrary", methods=["POST", "GET"])
def savelibrary():
    return server.saveLibrary(request) 

#Tries to login the current user
@application.route("/login", methods=["POST", "GET"])
def login():
    return server.login() 

#Updates a schedule variable
@application.route("/updateschedule", methods=["POST", "GET"])
def updateschedule():
    return server.updateSchedule()    

#Creates a new schedule
@application.route("/createschedule", methods=["POST", "GET"])
def createschedule():
    return server.createSchedule()
    
@application.route("/plantstream", methods=["POST", "GET"])
def plantstream():
    if (not server.isTokenValid(request)):
        return "InvalidToken"
    print os.getpid()
    return Response(server.streamPlantData(), mimetype="text/event-stream")

@application.route("/schedulestream", methods=["POST", "GET"])
def schedulestream():
    if (not server.isTokenValid(request)):
        return "InvalidToken"
    print os.getpid()
    return Response(server.streamScheduleData(), mimetype="text/event-stream")

@application.route("/")
def index():
    return server.app.send_static_file("index.html")

@application.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)


if __name__ == "__main__":
    #Start with gunicorn -k gevent -w 16 -b 192.168.130.46:80 test
    server.start()
    #parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    #parser.add_argument("-H", "--host", default="127.0.0.1", help="Server port")
    #parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    #args = parser.parse_args()
    server.info()    
