#!/usr/bin/env python
__copyright__ = """
    Copyright 2017 F4E | European Joint Undertaking for ITER and
    the Development of Fusion Energy ('Fusion for Energy').
    Licensed under the EUPL, Version 1.1 or - as soon they will be approved
    by the European Commission - subsequent versions of the EUPL (the "Licence")
    You may not use this work except in compliance with the Licence.
    You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
 
    Unless required by applicable law or agreed to in writing, 
    software distributed under the Licence is distributed on an "AS IS"
    basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
    or implied. See the Licence permissions and limitations under the Licence.
"""
__license__ = "EUPL"
__author__ = "Andre' Neto"
__date__ = "17/11/2017"

##
# Standard imports
##
import argparse
from flask import Flask, Response, request, send_from_directory
import json
import logging
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
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class WServer:
    """ TODO
    """

    #Synchronised queue between the SSE stream_data and stream_schedule_data functions. One queue per consumer thread. Should be further protected with semaphores
    threadPlantQueues = {}
    threadScheduleQueues = {}

    #IPC using UDP sockets
    UDP_BROADCAST_PORT = 23450
    udpQueue = BroacastQueue(UDP_BROADCAST_PORT) 

    def __init__(self, serverImpl, staticFolder, debug = False):
        """ TODO
        """
        #The web app which is a Flask standard application
        self.app = Flask(__name__, static_folder=staticFolder, static_url_path="")
        self.app.debug = debug

        self.LOGIN_TIMEOUT = 3600
        #Clean dead threads
        self.alive = True
        self.loginMonitorThread = threading.Thread(target=self.loginMonitor)
        self.serverImpl = serverImpl

    def start(self):
        """ TODO
        """
        #To force the killing of the threadCleaner thread with Ctrl+C
        self.loginMonitorThread.daemon = True
        self.loginMonitorThread.start()

    def threadCleaner(self):
        """ TODO
        """
        while self.alive:
            time.sleep(5)
            #Logout all the users that have not interacted with the server for a while
            currentTime = int(time.time())
            #db.query("DELETE FROM logins WHERE (" + str(currentTime) + " - last_interaction_time) > " + str(LOGIN_TIMEOUT));
            #TODO call the wserver implementation to logout user
       
    def isTokenValid(self, request):
        """ Verifies if a given token is valid.
            A token is valid iff a user has been properly validated.
        Args:
            request.form["token"]: a token generated after a successful user login.
        Returns:
            True if the token is valid.
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
        """ Streams data back to the client using SSE.
            The inferface is provided by a broadcastqueue.
            TODO encode mechanism to stop streaming @ user logout
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
                        if ("scheduleUID" in encodedPy):
                            if (encodedPy["tid"] == tid):
                                encodedJson = ""
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            log.critical("streamData failed {0}".format(e))
            self.streamData()

    
    def getVariablesInfo(self, request):
        """ Returns the all the available information for any of the requestedVariables.

        Args:
           request.form["pageName"]: name of the page (which corresponds to the name of the configuration).
           request.form["variables"]: identifiers of the variables to be queried.
        Returns:
            A json encoded list of variables or InvalidToken if the token is not valid.
            The following information is retrieved for any given variable:
            - name: the full variable name (containing any structure naming information, encoded as a @ separated name);
            - alias: a free format text which provides a meaningful name to the variable.
            - type as one of: uint8, int8, uint16, int16, uint32, int32, uint64, int64, string;
            - numberOfElements: as an array where each entry contains the number of elements on any given direction; 
            - description: one-line description of the variable;
            - permissions: user groups that are allowed to change this variable;
            - value: string encoded variable value.
            - and * N member variables (with the information above) if the variable being returned is structured.
        """
       
        toReturn = ""
        try: 
            pageName = request.form["pageName"]
            requestedVariables = json.loads(request.form["variables"])
            variables = self.serverImpl.getVariablesInfo(pageName, requestedVariables)
            variablesStr = [v.asSerializableDict() for v in variables]
            toReturn = json.dumps(variablesStr)
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"

        return toReturn 

    def updatePlant(self, request):
        """ Updates the values of the requested variables in the plant.
            All the variables that are successfully updated will be streamed to all the clients.

        Args:
            request.form["pageName"]: name of the page (which corresponds to the name of the configuration).
            request.form["tid"]: the unique thread (and process) identifier which was returned to the client when registered to the data stream (see streamData).
            request.form["variables"]: a dictionary with the list of variables to be updated in the form {variableName1:variableValue1, ...}
        Returns:
            The string ok if the values are successfully updated.
        """
        toReturn = "ok"
        try:
            pageName = request.form["pageName"]
            variables = request.form["variables"]
            variablesToUpdate = json.loads(variables)
            toStream = {
                "tid": request.form["tid"],
                "variables": []
            }
            variablesToStream = self.serverImpl.updatePlant(pageName, variablesToUpdate)
            toStream["variables"] = variablesToStream
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
           request.form["scheduleUID"]: TODO 
        Returns:
            TODO
        """
        toReturn = ""
        try: 
            scheduleUID = request.form["scheduleUID"]
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
            A json dictionary in the form  {variableName1:variableValue1, ...} with each schedule variable.
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
        """Logs a user into the system.
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

    def logout(self, request):
        """ Logs out a user from the system.
       
        Args:
           request.form["token"]: the token associated to the user being logged out.
        Returns:
            ok if the user is successfully logged out
        """
        token = request.form["token"]
            username = request.form["username"]
            log.debug("Logging out user with token: {0}".format(token))
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
        """ Updates other users of the same schedule that the variable values have changed. Note that these changes are not sync into the disk.
   
        Args:
            request.form["scheduleUID"]: unique schedule identifier.
            request.form["tid"]: the unique thread (and process) identifier which was returned to the client when registered to the data stream (see streamData).
            request.form["variables"]: a dictionary with the list of variables to be updated in the form {variableName1:variableValue1, ...}

        Returns:
            ok if the schedule is successfully updated or an empty string otherwise.
        """
        toReturn = ""
        try: 
            tid = request.form["tid"]
            scheduleUID = request.form["scheduleUID"]
            variables = json.loads(request.form["variables"])

            toStream = {
                "tid": tid,
                "scheduleUID": scheduleUID,
                "variables": variables 
            }
            self.udpQueue.put(json.dumps(toStream))
            toReturn = "ok"
        except KeyError as e:
            log.critical(str(e))
            toReturn = "InvalidParameters"
        return toReturn

    def commitSchedule(self, request):
        """ Updates the variable values for a given schedule. Note that these changes are not sync into the disk.
   
        Args:
            request.form["scheduleUID"]: unique schedule identifier.
            request.form["tid"]: the unique thread (and process) identifier which was returned to the client when registered to the data stream (see streamData).
            request.form["variables"]: a dictionary with the list of variables to be updated in the form {variableName1:variableValue1, ...}

        Returns:
            ok if the schedule is successfully updated or an empty string otherwise.
        """
        toReturn = ""
        try: 
            tid = request.form["tid"]
            scheduleUID = request.form["scheduleUID"]
            variables = json.loads(request.form["variables"])

            toStream = {
                "tid": tid,
                "scheduleUID": scheduleUID,
                "variables": self.serverImpl.commitSchedule(tid, scheduleUID, variables)
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

