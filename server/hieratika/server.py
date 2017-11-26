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
from abc import ABCMeta, abstractmethod
import ConfigParser
import datetime
import json
import logging
import multiprocessing
import os
import time
import threading
import uuid

##
# Project imports
##
from hieratika.util.broadcastqueue import BroacastQueue

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class HieratikaServer(object):
    """ TODO 
        TODO will have to decouple login management from parameter management. The same backend might be used in two places with different user authentication strategies.
    """
    
    __metaclass__ = ABCMeta

    def __init__(self):
        #Must be multiprocessing safe
        self.manager = multiprocessing.Manager()
        self.tokens = self.manager.dict()
        

    def loadCommon(self, config):
        """ Loads parameters that are common to all server implementations.
        
        Args:
            config (ConfigParser): parameters that are common to all server implementations:
            - udpBroadcastPort (int): the port that is used by the broadcastqueue.
            - loginMonitorUpdateRate (int): the time interval in seconds at which the state of logged in users is to be checked. 
            - loginMonitorMaxInactivityTime (int): maximum time that a given user can stay logged in without interacting with the server.
            - loginMaxUsers (int): maximum number of users that can be logged in at any time.
        Returns:
            True if all the parameters are successfully loaded.
        """
        try:
            #IPC using UDP sockets
            udpGroup = config.get("hieratika", "udpBroadcastGroup")
            udpPort = config.getint("hieratika", "udpBroadcastPort")
            self.udpQueue = BroacastQueue(udpGroup, udpPort)
            #For monitoring user login state
            self.loginMonitorThread = threading.Thread(target=self.loginMonitor)
            self.loginMonitorUpdateRate = config.getint("hieratika", "loginMonitorUpdateRate")
            self.loginMonitorMaxInactivityTime = config.getint("hieratika", "loginMonitorMaxInactivityTime")
            self.loginMaxUsers = config.getint("hieratika", "loginMaxUsers")
            #This allow to interrupt the sleep
            self.loginMonitorEvent = threading.Event()
        except (KeyError, ValueError, ConfigParser.Error) as e:
            log.critical("Failed to load configuration parameters {0}".format(e))
            return False
        return True

    def isTokenValid(self, tokenId):
        """ Returns true if the token is valid (i.e. if it was created against a valid login).
            If the token is valid the last time at which this token was checked is updated.

        Args:
            tokenId (str): the token to verify.           
 
        Returns:
            True if the token is valid.
        """
        ok = (tokenId in self.tokens)
        if (ok):
            self.tokens[tokenId]["lastInteraction"] = int(time.time())
        return ok

    def loginMonitor(self):
        """ Monitors login state of users and logsout users that have not interacted with the system for a while
        """
        while (not self.loginMonitorEvent.is_set()):
            self.loginMonitorEvent.wait(self.loginMonitorUpdateRate)
            #Logout all the users that have not interacted with the server for a while
            currentTime = int(time.time())
            #Dict proxys cannot be iterated like a normal dict
            keys = self.tokens.keys()
            for k in keys:
                if ((currentTime - self.tokens[k]["lastInteraction"])  > self.loginMonitorMaxInactivityTime):
                    log.info("User {0} was not activite for the last {1} seconds. User will be logout".format(self.tokens[k]["user"], self.loginMonitorMaxInactivityTime))
                    self.logout(k) 
            #Print current server info
            self.printInfo()


    def login(self, username):
        """ Tries to log a new user into the system.
            If successful a token will be associated to this user and registered into the system, so a subsequent call to
            isTokenValid, with this token, will return True.

        Returns:
            A User instance associated to a token described as a 32-character hexadecimal string or None if the login fails.
        """
        ok = (len(self.tokens) < self.loginMaxUsers)
        if (ok):
            ok = self.authenticate(username)
            user = None
            if (ok):
                user = self.getUser(username) 
                ok = (user is not None)
            if (ok):
                log.info("{0} logged in successfully".format(username))
                loginToken = uuid.uuid4().hex
                self.tokens[loginToken] = {"user": username, "lastInteraction": int(time.time())}
                user.setToken(loginToken)
            else:
                log.warning("{0} is not registered as a valid user".format(username))
        else:
            log.critical("Could not register {0} . No more users allowed to register into the system (max number is: {1})".format(username, self.loginMaxUsers))
            self.printInfo()
           
        return user

    def getTid(self):
        """
        Returns:
            A keyword which univocally identifies both the process and the thread.
        """
        tid = str(os.getpid())
        tid += "_"
        tid += str(threading.current_thread().ident) 
        return tid
 
    def printInfo(self):
        """ Prints information about the server state into the log.
        """
        serverInfo = "Server information\n"
        serverInfo = serverInfo + "Logged users\n"
        serverInfo = serverInfo + "{0:40}|{1:40}\n".format("user", "Last interaction")
        keys = self.tokens.keys()
        for k in keys:
            user = self.tokens[k]["user"]
            interactionTime = str(datetime.datetime.fromtimestamp(self.tokens[k]["lastInteraction"]))
            serverInfo = serverInfo + "{0:40}|{1:40}\n".format(user, interactionTime)
        log.info(serverInfo)

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

    def queueStreamData(self, jSonData):
        """ Streams the input jSonData to all the SSE registered clients. This data contains the id of the client thread (received the first time the client registered in streamData), the scheduleUID related to the update and a dictionary with the list of variables that were update. If the update is from the plant the tid and scheduleUID parameters are ignored.
        
        Args 
            jSonData (json): the data to be streamed in the format {tid: threadIdWhichTriggeredTheUpdate, scheduleUID:idOfScheduleWhichTriggeredTheUpdate, variables:{varibleName1:variableValue1, ...}}
        """
        self.udpQueue.put(jSonData)

    def start(self):
        """ Starts the login monitoring thread.
        """
        #To force the killing of the threadCleaner thread with Ctrl+C
        log.info("Starting login monitoring thread")
        self.loginMonitorThread.daemon = True
        self.loginMonitorThread.start()

    def stop(self):
        log.info("Stopping login monitoring thread")
        self.loginMonitorEvent.set()
        self.loginMonitorThread.join()
        log.info("Stopped login monitoring thread")


    def logout(self, token):
        """ Logsout the user identified with the given token from the system.

        Args:
            token (str): token that was provided to the user when was logged in
        """
        try:
            user = self.tokens[token]["user"]
            log.info("Logging out {0} with token {1}".format(user, token))
            del(self.tokens[token])
        except KeyError as e:
            log.critical("Failed to logout user with token {0} : {1}".format(token, e))


    @abstractmethod
    def getUser(self, username):
        """ 
        Args:
            username(str): the username of the user to get.
        Returns:
            The user associated to the given username or None if not found.
        """
        pass

    @abstractmethod
    def load(self, config):
        """ Configures the server against a set of parameters. This set of parameters is specific for each server implementation.
        Args:
            config(ConfigParser): the server specific implementation parameters are in the section "server-impl".
        Returns:
            True if the server is successfully configured.
        """
        pass

    @abstractmethod 
    def authenticate(self, username):
        """ Authenticates a user into the system.
            Returns:
                True if the user is successfully authenticated.
        """
        pass

    @abstractmethod
    def getVariablesInfo(self, pageName, requestedVariables):
        """ Returns the all the available information for any of the requestedVariables.

        Args:
           pageName (str): name of the page (which corresponds to the name of the configuration).
           variables ([str]): identifiers of the variables to be queried.
        Returns:
            A list of Variables ([Variable]) with all the information available for each of the request variables 
        """
        pass

    @abstractmethod
    def getSchedules(self, username, pageName):
        """ Gets all the schedules that are avaiable for a given user in a given page.

        Args:
           username: the username to which the returned schedules belong to. 
           pageName: the name of the page associated to the schedule.
        Returns:
            An array with all the schedules that are available for the requested user in the 
            specified page.
        """
        pass

    @abstractmethod
    def getUsers(self):
        """
        Returns:
            All the system users.
        """
        pass

    @abstractmethod
    def getPages(self):
        """
        Returns:
            All the pages that are available.
        """
        pass

    @abstractmethod
    def getPage(self, pageName):
        """Gets the page associated to a given name

           Args:
               token (str): the page name to query.

           Returns:
               The Page or None if the name is not found.
        """
        pass

    @abstractmethod
    def getSchedule(self, scheduleUID):
        """ TODO define schedule structure

        Args:
            scheduleUID (str): unique schedule identifier.
        Returns:
            Information about the requested schedule.
        """
        pass

    @abstractmethod
    def getScheduleVariablesValues(self, scheduleUID):
        """ Gets all the variables values associated to a given schedule.
        
        Args:
            scheduleUID(str): unique schedule identifier.
        Returns:
            A dictionary of variableId:variableValue pairs  
        pass
        """

    @abstractmethod
    def commitSchedule(self, tid, scheduleUID, variables):
        """ Permanently updates the requested variable values for a given schedule. 
    
        Args:
            tid (str): unique identifier of the calling thread/process
            scheduleUID (str): unique schedule identifier
            variables ({variableName1:value1, variableName2:value2, ...}):  dictionary with variables to be updated.

        Returns:
            The list of variables that were updated in the form of a dictionary {variableName1:value1, variableName2:value2, ...}
        """
        pass

    @abstractmethod
    def updatePlant(self, pageName, variables):
        """ Updates the variable values of the plant (associated to a given page).
    
        Args:
            pageName (str): name of the page holding these variables.
            variables ({variableName1:value1, variableName2:value2, ...}):  dictionary with variables to be updated.

        Returns:
            The list of variables that were updated in the form of a dictionary {variableName1:value1, variableName2:value2, ...}
        """
        pass

    @abstractmethod
    def createSchedule(self, name, description, username, pageName, sourceScheduleUID = None):
        """ Creates a new schedule either based on a existing schedule (if sourceSchedule is not None) or from the plant. 

        Args:
            name (str): the name of the schedule to create.
            description (str): the description of the schedule to create.
            username (str): the owner of the schedule.
            pageName (str): name of the page to which the schedule belongs to.
            sourceScheduleUID (str): create the schedule by copying from the schedule with this unique identifier. If sourceScheduleUID is None, copy from the plant.

        Returns:
            The unique identifier of the created schedule or None if the schedule could not be created.
        """
        pass

