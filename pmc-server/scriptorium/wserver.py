#!/usr/bin/python

##
# Standard imports
##
import argparse
from flask import Flask, Response, request, send_from_directory
import json
import logging
import multiprocessing 
import os
import time
import timeit
import threading

##
# Project imports
##
from scriptorium.util.broadcastqueue import BroacastQueue
from scriptorium.page import Page
from scriptorium.user import User
from scriptorium.usergroup import UserGroup

##
# Defines
##
#Maximum time that a user is allowed to be logged in without interacting with the database
LOGIN_TIMEOUT = 3600
UDP_BROADCAST_PORT = 23450

log = logging.getLogger("{0}".format(__name__))

class WServer:
    """ TODO
    """

    # TODO CLEAN
    #This function allocates a DB instance for any given thread
    allThreads = []
    alive = True

    #Synchronised queue between the SSE stream_data and stream_schedule_data functions. One queue per consumer thread. Should be further protected with semaphores
    threadPlantQueues = {}
    threadScheduleQueues = {}

    #IPC using UDP sockets
    udpQueue = BroacastQueue(UDP_BROADCAST_PORT) 

    def __init__(self, serverImpl, staticFolder, debug = False):
        """ TODO
        """
        #The web app which is a Flask standard application
        self.app = Flask(__name__, static_folder=staticFolder, static_url_path="")
        self.app.debug = debug

        #Clean dead threads
        self.monitorThread = threading.Thread(target=self.threadCleaner)
        self.serverImpl = serverImpl

    def start(self):
        """ TODO
        """
        #To force the killing of the threadCleaner thread with Ctrl+C
        self.monitorThread.daemon = True
        self.monitorThread.start()


    #Cleans the threadPlantQueues and threadScheduleQueues 
    def threadCleaner(self):
        while self.alive:
            time.sleep(5)
            for t in self.allThreads:
                if (not t.isAlive()):
                    tid = str(t)
                    self.allThreads.remove(t)
                    #Do not delete the MainThread!
                    if ("MainThread" not in tid):
                        self.threadPlantQueues.pop(tid, None)
                        self.threadScheduleQueues.pop(tid, None)
            #Clean all the users that have not interacted with the wserver for a while
            currentTime = int(time.time())
            #db.query("DELETE FROM logins WHERE (" + str(currentTime) + " - last_interaction_time) > " + str(LOGIN_TIMEOUT));
            #TODO call the wserver implementation to logout user
       
    def isTokenValid(self, request):
        """ TODO
        """
        if (request.method == "POST"):
            ok = ("token" in request.form)
            if (ok):
                tokenId = request.form["token"]
        else:
            ok = ("token" in request.args)
            if (ok):
                tokenId = request.args["token"]
        if (ok): 
            ok = self.serverImpl.isTokenValid(tokenId)
            log.debug("Token: {0} is {1}".format(tokenId, str(ok)))
        return ok

    def getTid(self):
        """
            Returns:
                A keyword which univocally identifies both the process and the thread.
        """
        tid = str(os.getpid())
        tid += "_"
        tid += str(threading.current_thread().ident) 
        return tid

    def streamData(self):
        """ TODO
        """
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
                        if ("scheduleName" in encodedPy):
                            if (encodedPy["tid"] == tid):
                                encodedJson = ""
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            print "Exception ignored"
            print e
            #ignore
        print "BYE!!"

    
    def getPlantInfo(self, request):
        """ Returns all the variables information related to any set of plants.
            See getVariableInfo for details about the variable information.  

        Args:
           request.form["pageName"]: name of the page (which corresponds to the name of the configuration).
           request.form["variables"]: identifiers of the variables to be queried.
        Returns:
            A json encoded list of variables or InvalidToken if the token is not valid.
            The following information is retrieved for any given variable:
            - type as one of: uint8, int8, uint16, int16, uint32, int32, uint64, int64, string;
            - numberOfElements: as an array where each entry contains the number of elements on any given direction; 
            - name: the full variable name (containing any structure naming information);
            - variableId: same as name. TODO: deprecate;
            - description: one-line description of the variable;
            - permissions: user groups that are allowed to change this variable;
            - value: string encoded variable value.
        """
       
        toReturn = ""
        try: 
            pageName = request.form["pageName"]
            requestedVariables = json.loads(request.form["variables"])
            variables = self.serverImpl.getPlantInfo(pageName, requestedVariables)
            toReturn = json.dumps(variables)
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"

        return toReturn 

    def submit(self, request):
        """ TODO
        """
        toReturn = "done"
        try:
            update = request.form["update"]
            variablesToUpdate = json.loads(update)
            toStream = {
                "tid": request.form["tid"],
                "variables": []
            }
            variablesToStream = self.serverImpl.updatePlant(variablesToUpdate)
            #TODO take care of security
            toStream["variables"] = variablesToUpdate
            self.udpQueue.put(json.dumps(toStream))
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def getSchedules(self, request):
        """ Gets all the schedules that are avaiable for a given user in a given page.

        Args:
           request.form["username"]: the username to which the returned schedules belong to. 
           request.form["pageName"]: the name of the page associated to the schedule.
        Returns:
            A json representation of all the schedules that are available for the requested user in the 
            specified page.
        """
        toReturn = ""
        try:
            pageName = request.form["pageName"]
            if "username" in request.form:
                username = request.form["username"]
            else:
                username = ""
            
            schedules = self.serverImpl.getSchedules(username, pageName)
            print schedules
            schedulesStr = [s.__dict__ for s in schedules]
            toReturn = json.dumps(schedulesStr)
            log.debug("For {0} in {1} returning: {2}".format(username, pageName, toReturn))
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def getUsers(self, request):
        """
        Returns:
            All the system users.
        """
        users = self.serverImpl.getUsers()
        usersStr = [u.asSerializableDict() for u in users]
        log.debug("Returning users: {0}".format(usersStr))
        toReturn = json.dumps(usersStr)
        return toReturn

    def getPages(self, request):
        """
        Returns:
            All the pages that are available.
        """
        pages = self.serverImpl.getPages()
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

        try: 
            pageName = request.form["pageName"]
            log.debug("Looking for page: {0}".format(pageName))
            page = self.serverImpl.getPage(pageName)
            log.debug("Returning page: {0}".format(str(page)))
            toReturn = json.dumps(page.__dict__)
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def getSchedule(self, request):
        """ TODO 
        Args:
           request.form["scheduleName"]: TODO 
        Returns:
            TODO
        """
        toReturn = ""
        try: 
            scheduleName = request.form["scheduleName"]
            toReturn = json.dumps(schedule)
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def getScheduleVariablesValues(self, request):
        """ Gets all the variables values for a given schedule (identified by its id which is the path to the file).
        
        Args:
            request.form["scheduleUID"]: the schedule identifier.
    
        Returns:
            A json array with a variable:value pair for each schedule variable.
        """
        try: 
            variables = []
            scheduleUID = request.form["scheduleUID"]
            variables = self.serverImpl.getScheduleVariablesValues(scheduleUID)
            toReturn = json.dumps(variables)
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def login(self, request):
        """Logs an user into the system.
           Note that the same user might be logged from different locations. One authentication token will 
           be generate for each login.
           
           Args:
               request.form["username"]: shall contain the username.
    
           Returns:
               A json representation of the User.
        """
        try: 
            username = request.form["username"]
            log.debug("Logging in: {0}".format(username))
            user = self.serverImpl.login(username)
            if (user is not None):
                user = user.asSerializableDict()
            else:
                user = {"username":""}
            toReturn = json.dumps(user)
            log.debug("{0}".format(str(user)))
        except KeyError as e:
            log.critical("Missing username ({0})".format(e))
            toReturn = "InvalidParameters"
        return toReturn

    def updateSchedule(self, request):
        """ Updates the variable values for a given schedule. Note that these changes are not sync into the disk.
    
        Args:
            request.form["update"] (json): containing {scheduleName: pathToXmlFile, values = [{id:val, ...}]}

        Returns:
            ok if the schedule is successfully updated or an empty string otherwise.
        """
        toReturn = ""
        try: 
            update = request.form["update"]
            update = json.loads(update)
            scheduleName = update["scheduleName"]
            variables = update["variables"]
            tid = update["tid"]

            toStream = {
                "tid": tid,
                "scheduleName": scheduleName,
                "variables": self.serverImpl.updateSchedule(tid, scheduleName, variables)
            }
            self.udpQueue.put(json.dumps(toStream))
            toReturn = "ok"
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def createSchedule(self, request):
        """ TODO
        """
        try:
            name = request.form["name"]
            description = request.form["description"]
            username = request.form["username"]
            pageName = request.form["pageName"]
            self.serverImpl.createSchedule(name, description, username, pageName) 
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def info(self):
        print "TODO ADD info (console and http)"

