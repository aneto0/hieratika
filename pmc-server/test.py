#!/usr/bin/python

import argparse
import threading
from multiprocessing import Process
import os
import epics
from epics import caget, caput, camonitor
import time
import json
import uuid
import numpy
from flask import Flask, Response, request, send_from_directory
from broadcastqueue import *

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
UDP_BROADCAST_PORT = 23450

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
    udpQueue = BroacastQueue(UDP_BROADCAST_PORT) 

    def __init__(self):
        epics.ca.find_libca()
        db = self.getDB()
        variables = db["variables"]
        for variable in variables:
            if variable["isLiveVariable"] == 1:
                pvName = variable["id"]
                camonitor(pvName, None, pvValueChanged)

        #Clean dead threads
        self.monitorThread = threading.Thread(target=self.threadCleaner)

    def start(self):
        #To force the killing of the threadCleaner thread with Ctrl+C
        self.monitorThread.daemon = True
        self.monitorThread.start()

        self.app.debug = True
        #Running a threaded Flask is ok only for debugging
        #app.run(threaded=False, host=args.host, port=args.port)
        #self.app.run(host='0.0.0.0')
        #self.alive = False

    def getDB(self):
        ct = threading.current_thread()
        tid = self.getTid()
        if tid not in self.threadDBs:
            self.threadDBs[tid] = dataset.connect('sqlite:////tmp/pmc-server.db')
            if (ct not in self.allThreads):
                self.allThreads.append(threading.current_thread())

        return self.threadDBs[tid]

    def getTid(self):
        tid = str(os.getpid())
        tid += "_"
        tid += str(threading.current_thread().ident) 
        return tid

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
            #db.query("DELETE FROM logins WHERE (" + str(currentTime) + " - last_interaction_time) > " + str(LOGIN_TIMEOUT));
       
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
        return True

    def updateScheduleVariablesDB(self, variableId, scheduleId, variableValue):
        db = self.getDB()
        scheduleVariables = db["schedule_variables"]
        row = {
            "variable_id": variableId,
            "schedule_id": scheduleId,
            "value": pickle.dumps(variableValue)
        }
        scheduleVariables.upsert(row, ["variable_id", "schedule_id"])
        return True

    def streamData(self):
        tid = None
        try:
            while True:
                if (tid == None):
                    # The first time just register the Queue and send back the TID so that updates from this client are not sent back to itself (see updateschedule)
                    tid = self.getTid()
                    encodedPy = {"reset": True, "tid": tid}
                    encodedJson = json.dumps(encodedPy)
                else:
                    # Monitor on change
                    encodedJson = self.udpQueue.get()
                    if (encodedJson == None):
                        encodedJson = ""
                        time.sleep(0.01)
                    else:
                        encodedPy = json.loads(encodedJson)
                        # Only trigger if the source was not from this tid. If it an update from 
                        # the plant, always trigger as some of the parameters might have failed to load
                        if ("scheduleId" in encodedPy):
                            if (encodedPy["tid"] == tid):
                                encodedJson = ""
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            print "Exception ignored"
            print e
            #ignore
        print "BYE!!"

    def rowToVariable(self, row, validations, permissions):
        """Parses an sql row result into a proper variable structure (mostly needed to handle the pickle of value)
        """
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

    def isArray(self, numberOfElements):
        """Helper function to check if a given variable is an array
        """
        variableIsArray = (len(numberOfElements) > 1)
        if (not variableIsArray):
            variableIsArray = (numberOfElements[0] > 1)
        return variableIsArray


    def getMaxLinearIndex(self, numberOfElements):
        """Computes the maximum index in a multi-dimensional array
           by multiplying all the dimensions
        """
        maxIdx = 1
        for i,val in enumerate(numberOfElements):
            maxIdx = maxIdx * numberOfElements[i]
        return maxIdx

    def getDividers(self, numberOfElements):
        """Helper function for the transformation of a multi-dimensional
           array into a linear one dimensional array
        """
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

    def setAtArrayIndex(self, ret, variableId, value):
        """Updates the ret multi-dimensional array with the input value.
           The index in the multi-dimensional array is retrieved by parsing the variable id
           e.g. VAR@3,4,2,3 => [3][4][2][3] in a 4-dim array
        """
        idxs = variableId.split("@")[-1].split(",")
        for k, idx in enumerate(idxs):
            if (k < (len(idxs) - 1)):
                ret = ret[int(idx)]
            else:
                ret[int(idx)] = value

    def getVariableInfo(self, variableId, variables, validations, permissions):
        """Recursive function which retrieves the information of any multi-dimensional variable structure
        """
        db = self.getDB()
        #statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id'" + variableId + "'"
        row = variables.find_one(id=variableId)
        if (row["numberOfElements"] != ""):
            variableNumberOfElements = pickle.loads(row["numberOfElements"])
        else:
            variableNumberOfElements = []
        #variableIsArray = self.isArray(variableNumberOfElements) 
        variableIsStruct = row["isStruct"]
        ret = self.rowToVariable(row, validations, permissions)
        if (variableIsStruct): 
            #if (variableIsArray):
            #    ret = numpy.empty(variableNumberOfElements).tolist()
            #statement = "SELECT DISTINCT(id), numberOfElements, value, isStruct FROM variables WHERE id LIKE '" + variableId + "@%' AND id NOT LIKE '" + variableId + "@%@%'"
            statement = "SELECT * FROM variables WHERE id LIKE '" + variableId + "@%' AND id NOT LIKE '" + variableId + "@%@%'"
            for row in db.query(statement):
                memberNumberOfElements = pickle.loads(row["numberOfElements"])
                variableId = row["id"]
                memberId = variableId.split("@")[-1]
                memberIsStruct = row["isStruct"]
                memberIsArray = self.isArray(memberNumberOfElements)
                if (memberIsStruct):
                    if (memberIsArray):
                        appendTo = numpy.empty(memberNumberOfElements).tolist()
                        #if (variableIsArray):
                        #    self.setAtArrayIndex(ret, variableId, appendTo)
                        #else:
                        ret[memberId] = appendTo
                        idxStr = ""
                        maxIdx = self.getMaxLinearIndex(memberNumberOfElements)
                        dividers = self.getDividers(memberNumberOfElements)
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
                                    self.setAtArrayIndex(appendTo, variableIdIdx, self.getVariableInfo(variableIdIdx, variables, validations, permissions))
                                    idxStr = ""
                                j = j + 1
                            i = i + 1
                    else:
                        #if (variableIsArray):
                        #    self.setAtArrayIndex(ret, variableId, self.getVariableInfo(variableId, variables, validations, permissions))
                        #else:
                        ret[memberId] = self.getVariableInfo(variableId, variables, validations, permissions)
                else:
                    #if (variableIsArray):
                        #setAtArrayIndex(ret, variableId, pickle.loads(row["value"]))
                    #    self.setAtArrayIndex(ret, variableId, self.rowToVariable(row, validations, permissions))
                    #else:
                        #ret[memberId] = pickle.loads(row["value"])
                    ret[memberId] = self.rowToVariable(row, validations, permissions)       
        #else:
            #return pickle.loads(row["value"]) 
            #return self.rowToVariable(row, validations, permissions) 
        return ret


    def getPlantInfo(self, request):
        db = self.getDB()
        variables = db["variables"]
        validations = db["validations"]
        permissions = db["permissions"]
        toReturn = ""
       
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        elif ("variables" not in request.form):
            toReturn = "InvalidParameters"
        else: 
            requestedVariables = request.form["variables"]
            jSonRequestedVariables = json.loads(requestedVariables)
            encodedPy = {"variables": [] }
            for variableId in jSonRequestedVariables:
                variable = self.getVariableInfo(variableId, variables, validations, permissions)
#                 variable = variables.find_one(id=variableId)
#                 if (variable is not None):
#                     variable["variableId"] = variable["id"]  
#                     variable["library"] = (variable["library"] == 1)
#                     variable["initialValue"] = pickle.loads(variable["initialValue"])  
#                     variable["value"] = pickle.loads(variable["value"])  
#                     variable["numberOfElements"] = pickle.loads(variable["numberOfElements"])  
#                     variable["validation"] = []  
#                     validation = validations.find(variable_id=variable["id"])
#                     for v in validation:
#                         variable["validation"].append({
#                             "description": v["description"],
#                             "fun": v["fun"],
#                             "parameters": pickle.loads(v["parameters"])
#                         })
# 
#                     variable["permissions"] = []
#                     permission = permissions.find(variable_id=variable["id"])
#                     for p in permission:
#                         variable["permissions"].append(p["group_id"])
                encodedPy["variables"].append(variable) 
            

            toReturn = json.dumps(encodedPy)
        return toReturn 

    def submit(self, request):
        toReturn = "done"
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        elif ("update" not in request.form):
            toReturn = "InvalidParameters"
        else: 
            updateJSon = request.form["update"]
            jSonUpdateVariables = json.loads(updateJSon)
            toStream = {
                "tid": request.form["tid"],
                "variables": []
            }
            for variableId in jSonUpdateVariables.keys():
                newValue = jSonUpdateVariables[variableId]
                if(self.updatePlantVariablesDB(variableId, newValue)):
                    toStream["variables"].append({"variableId" : variableId, "value" : newValue})
                #Warn others that the plant values have changed!
                #for k, q in threadPlantQueues.iteritems():
                #    jsonToSend = json.dumps("variables": [ {"variableId" : variableId, "value" : newValue}]) 
            #TODO must check what values were actually updated
            #TODO take care of security
            self.udpQueue.put(json.dumps(toStream))
            #caput(k, request.args[k])
        return toReturn

    def getSchedules(self, request):
        db = self.getDB()
        userId = ""
        schedules = []
        toReturn = ""
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
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
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            pmcLibVariables = json.loads(request.form["variables"])
            for variable in pmcLibVariables:
                libraries = tableLibraries.find(variable_id=variable)
                for library in libraries:
                    if variable in librariesNames:
                        librariesNames[variable]["ids"].append(
                            {
                                "id": library["id"],
                                "name": library["name"]
                            }
                        )
                    else:
                        librariesNames[variable] = {"variable":variable, "ids": [
                            {
                                "id": library["id"],
                                "name": library["name"]
                            }
                        ]}
            toReturn = json.dumps({"libraries": librariesNames.values()}) 
        return toReturn

    def getLibrary(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        librariesNames = {}
        tableLibraryVariables = db["libraryVariables"]
        variables = []
        toReturn = ""
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            variableId = request.form["variableId"]
            if("libraryId" in request.form):
                requestedLibraryId = request.form["libraryId"]
            else:
                requestedLibraryName = request.form["libraryName"]
                requestedLibraryUser = request.form["userId"]
                libraries = tableLibraries.find_one(name=requestedLibraryName, user_id=requestedLibraryUser, variable_id=variableId)
                requestedLibraryId = libraries["id"]

            libraryVariables = tableLibraryVariables.find(library_id=requestedLibraryId)
            for l in libraryVariables:
                lv = {
                    "variableId": l["variable_id"],
                    "value": pickle.loads(l["value"])
                } 
                variables.append(lv)
            toReturn = json.dumps(variables)
        return toReturn

    def saveLibrary(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        tableLibraryVariables = db["libraryVariables"]
        toReturn = ""
        #TODO Check if the library already exists (and in the future prevent it from being overwritten if was ever used)
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            library = {
                "name": request.form["libraryName"],
                "description": request.form["libraryDescription"],
                "user_id": request.form["userId"],
                "variable_id": request.form["variableId"]
            }
            tableLibraries.upsert(library, ["name", "variable_id", "user_id"])
            createdLibrary = tableLibraries.find_one(user_id=library["user_id"], name=library["name"], variable_id=library["variable_id"])

            requestedVariables = json.loads(request.form["variables"])
            for lv in requestedVariables: 
                value = {
                    "variable_id": lv["variableId"], 
                    "library_id": str(createdLibrary["id"]),
                    "value": pickle.dumps(json.loads(lv["value"]))
                }
                tableLibraryVariables.upsert(value, ["variable_id", "library_id"])
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
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            updateJSon = request.form["update"]
            jSonUpdateSchedule = json.loads(updateJSon)
            scheduleId = jSonUpdateSchedule["scheduleId"]
            values = jSonUpdateSchedule["values"]

            toStream = {
                "tid": jSonUpdateSchedule["tid"],
                "scheduleId": jSonUpdateSchedule["scheduleId"],
                "variables": []
            }
            for v in values:
                variableId = v["id"]
                value = v["value"]
                if(self.updateScheduleVariablesDB(variableId, scheduleId, value)):
                    toStream["variables"].append({"variableId" : variableId, "value" : value})
                    
                #Warn (only the!) others that the scheduler values have changed!
                #for k, q in threadScheduleQueues.iteritems():
                #    if (k != requesterTid):
                #        q.put((variableId, scheduleId, value), True)
            self.udpQueue.put(json.dumps(toStream))
            
            toReturn = "ok"
        return toReturn

    def createSchedule(self, request):
        db = self.getDB()
        schedulesTable = db["schedules"]
        toReturn = ""
        if (not self.isTokenValid(request)):
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
                db.query("DELETE FROM schedule_variables WHERE schedule_id='" + str(createdSchedule["id"]) + "' AND value=''")
                db.commit()
                
            toReturn = "ok"
        return toReturn

    def info(self):
        print "TODO ADD info (console and http)"

server = Server()
server.start()
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
    return server.updateSchedule(request)    

#Creates a new schedule
@application.route("/createschedule", methods=["POST", "GET"])
def createschedule():
    return server.createSchedule(request)
    
@application.route("/stream", methods=["POST", "GET"])
def stream():
    if (not server.isTokenValid(request)):
        return "InvalidToken"
    return Response(server.streamData(), mimetype="text/event-stream")

@application.route("/")
def index():
    return server.app.send_static_file("index.html")

@application.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)


if __name__ == "__main__":
    #Start with gunicorn -k gevent -w 16 -b 192.168.130.46:80 test
    
    #server.start()
    #parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    #parser.add_argument("-H", "--host", default="127.0.0.1", help="Server port")
    #parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    #args = parser.parse_args()
    server.info()    
