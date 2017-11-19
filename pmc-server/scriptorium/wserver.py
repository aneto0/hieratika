#!/usr/bin/python

##
# Standard imports
##
#TODO Clean imports
import argparse
from flask import Flask, Response, request, send_from_directory
import json
import multiprocessing 
import numpy
import threading
import os
import time
import timeit
import uuid
import logging
import dataset
import pickle

from xml.etree import cElementTree
from xml.dom import minidom
from lxml import etree

import os
import fnmatch

##
# Project imports
##
from util.broadcastqueue import BroacastQueue
from loginmanager import LoginManager 
from pagemanager import PageManager 
from xmlmanager import XmlManager 
from page import Page
from user import User
from usergroup import UserGroup

##
# Defines
##
#Maximum time that a user is allowed to be logged in without interacting with the database
LOGIN_TIMEOUT = 3600
UDP_BROADCAST_PORT = 23450

##
# The application base directory (i.e. where it expects to find the scriptorium configuration files)
##
PSPS_BASE_DIR = "demo"

##
# Global variables to be shared by all the processes schedule by gunicorn
# Note that gunicorn must be run with --preload, otherwise there will be a global variable instance for every process, which beats the purpose.
##
#XML namespaces
ns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
      "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

#The global managers
loginManager = LoginManager()
pageManager = PageManager()
xmlManager = XmlManager()
#TODO this path shall be loaded from the command line or from a configuration file
loginManager.load("config/users.xml")
pageManager.load("config/pages.xml")

#Logger configuration
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("scriptorium-{0}".format(__name__))

#The web app which is a Flask standard application
app = Flask(__name__, static_url_path="")
app.debug = True
#Running a threaded Flask is ok only for debugging
#app.run(threaded=False, host=args.host, port=args.port)
#self.app.run(host='0.0.0.0')
#self.alive = False

class Server:
    #A DB access cannot be shared between different threads.
    #This function allocates a DB instance for any given thread
    threadDBs = {}
    allThreads = []

    alive = True

    #Synchronised queue between the SSE stream_data and stream_schedule_data functions. One queue per consumer thread. Should be further protected with semaphores
    threadPlantQueues = {}
    threadScheduleQueues = {}

    #IPC using UDP sockets
    udpQueue = BroacastQueue(UDP_BROADCAST_PORT) 

    def __init__(self):
        #Clean dead threads
        self.monitorThread = threading.Thread(target=self.threadCleaner)

    def start(self):
        #To force the killing of the threadCleaner thread with Ctrl+C
        self.monitorThread.daemon = True
        self.monitorThread.start()


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
            ok = loginManager.isTokenValid(tokenId)
        log.debug("Token: {0} is {1}".format(tokenId, str(ok)))
        return ok

    def updatePlantVariablesDB(self, variableId, variableValue):
        #db = self.getDB()
        #variables = db["variables"]
        #row = variables.find_one(id=variableId)
        #if (row is not None):
        #    row["value"] = pickle.dumps(variableValue);
        #    variables.upsert(row, ["id"])
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

    def convertVariableTypeFromXML(self, xmlVariableType):
        #TODO move to helper module
        toReturn = "string"
        if (xmlVariableType == "recordDouble"):
            toReturn = "float64" 
        elif (xmlVariableType == "recordFloat"):
            toReturn = "float32" 
        elif (xmlVariableType == "recordString"):
            toReturn = "string" 
        return toReturn


    def getPlantInfo(self, request):
        """ Returns all the variables information related to any set of plants.
            See getVariableInfo for details about the variable information.  

        Args:
           request.form["pageName"]: name of the page (which corresponds to the name of the configuration).
           request.form["variables"]: identifiers of the variables to be queried.
        Returns:
            A json encoded list of variables or InvalidToken if the token is not valid.
        """

        toReturn = "InvalidParameters"
        if ("pageName" not in request.form):
            log.critical("No page name was set for getPlantInfo")
        else:
            pageName = request.form["pageName"]
            xmlFileLocation = "{0}/psps/configurations/{1}/000/plant.xml".format(PSPS_BASE_DIR, pageName)
            log.debug("Loading plant configuration from {0}".format(xmlFileLocation))
            perfStartTime = timeit.default_timer()
            toReturn = ""
           
            if (not self.isTokenValid(request)):
                toReturn = "InvalidToken"
            elif ("variables" not in request.form):
                toReturn = "InvalidParameters"
            else: 
                requestedVariables = request.form["variables"]
                jSonRequestedVariables = json.loads(requestedVariables)
                encodedPy = {"variables": [] }
                xmlManager.acquire(xmlFileLocation)
                for variableName in jSonRequestedVariables:
                    variable = xmlManager.getVariableInfo(variableName, xmlFileLocation)
                    if (variable is not None):
                        encodedPy["variables"].append(variable) 
                
                xmlManager.release(xmlFileLocation)
                perfElapsedTime = timeit.default_timer() - perfStartTime
                log.debug("Took {0} s to get the information for all the variables in the plant".format(perfElapsedTime))
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
        return toReturn

    def getAllFiles(self, pageId):
        #TODO move to helper module
        matches = []
        directory = "{0}/{1}".format(PSPS_BASE_DIR, pageId)
        print directory
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.xml'):
                if (filename != "plant.xml"):
                    matches.append(os.path.join(root, filename))
        return matches

    def getSchedules(self, request):
        userId = ""
        schedules = []
        toReturn = ""
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            pageId = request.form["pageId"]
            if "userId" in request.form:
                userId = request.form["userId"]
            else:
                userId = ""

            allSchedulesXML = self.getAllFiles(pageId)

            for xmlFile in allSchedulesXML:
                filePath = xmlFile.split("/")
                schedule = {
                    "id": xmlFile,
                    "name": filePath[-1],
                    "user_id": userId,
                    "description": "TBD",
                    "page_id": pageId
                }
                schedules.append(schedule);

            toReturn = json.dumps(schedules)
        return toReturn

    def getUsers(self, request):
        """
        Returns:
            All the system users.
        """
        toReturn = ""
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            users = loginManager.getUsers()
            usersStr = [u.asSerializableDict() for u in users]
            log.debug("Returning users: {0}".format(usersStr))
            toReturn = json.dumps(usersStr)
        return toReturn

    def getPages(self, request):
        """
        Returns:
            All the pages that are available.
        """
        toReturn = ""
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else:
            pages = pageManager.getPages()
            pagesStr = [p.__dict__ for p in pages]
            log.debug("Returning pages: {0}".format(pagesStr))
            toReturn = json.dumps(pagesStr)
        return toReturn

    def getPage(self, request):
        """
        Args:
           request.form["pageName"]: shall contain the page name.
        Returns:
            A page with a given name or InvalidToken if the token is not valid.
        """

        toReturn = ""
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            pageName = request.form["pageName"]
            log.debug("Looking for page: {0}".format(pageName))
            page = pageManager.getPage(pageName)
            log.debug("Returning page: {0}".format(str(page)))
            toReturn = json.dumps(page.__dict__)
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
        """ Gets all the variables values for a given schedule (identified by its id which is the path to the file).
        
        Args:
            request.form["scheduleId"]: the schedule identifier.
    
        Returns:
            A json array with a variable:value pair for each schedule variable.
        """
        toReturn = ""
        variables = []
        db = self.getDB()
        if (not self.isTokenValid(request)):
            toReturn = "InvalidToken"
        else: 
            requestedSchedule = request.form["scheduleId"]
            self.xmlManager.acquire(requestedSchedule)
            variables = self.xmlManager.getAllVariablesValue(requestedSchedule)
            self.xmlManager.release(requestedSchedule)
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
        tableLibraryVariables = db["library_variables"]
        variables = []
        toReturn = {"description":"", "variables":[]}
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

            toReturn["description"] = libraries["description"]
            libraryVariables = tableLibraryVariables.find(library_id=requestedLibraryId)
            for l in libraryVariables:
                lv = {
                    "variableId": l["variable_id"],
                    "value": pickle.loads(l["value"])
                } 
                toReturn["variables"].append(lv)
            toReturn = json.dumps(toReturn)
        return toReturn

    def saveLibrary(self, request):
        db = self.getDB()
        tableLibraries = db["libraries"]
        tableLibraryVariables = db["library_variables"]
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
            toReturn = json.dumps({"id":str(createdLibrary["id"])})
        return toReturn

    def login(self):
        """Logs an user into the system.
           Note that the same user might be logged from different locations. One authentication token will 
           be generate for each login.
           
           Args:
               request.form["username"]: shall contain the username.
    
           Returns:
               A json representation of the User.
        """
        user = {
            "username": ""
        }
        requestedUsername = request.form["username"]
        log.debug("Logging in: {0}".format(requestedUsername))
        token = loginManager.login(requestedUsername)
        if (len(token) != 0):
            user = loginManager.getUser(token)
            user = user.asSerializableDict()
            user["token"] = token
            
        log.debug("{0}".format(str(user)))
        return json.dumps(user)

    def updateSchedule(self, request):
        """ Updates the variable values for a given schedule. Note that these changes are not sync into the disk.
    
        Args:
            request.form["update"] (json): containing {scheduleId: pathToXmlFile, values = [{id:val, ...}]}

        Returns:
            ok if the schedule is successfully updated or an empty string otherwise.
        """
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
            xmlManager.acquire(scheduleId)
            for v in values:
                variableId = v["id"]
                value = v["value"]
                if(xmlManager.updateVariable(variableName, scheduleId, variableValue)):
                    toStream["variables"].append({"variableId" : variableId, "value" : value})
                    
            xmlManager.release(scheduleId)
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
    #Start with gunicorn --preload -k gevent -w 16 -b 192.168.130.46:80 test
    
    #server.start()
    #parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    #parser.add_argument("-H", "--host", vt="127.0.0.1", help="Server port")
    #parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    #args = parser.parse_args()
    server.info()    
