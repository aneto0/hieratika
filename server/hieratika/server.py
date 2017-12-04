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
    """ Abstract class for any server implementation.
        It implements the inter-client SSE streaming mechanism which allows to notify all the registered clients
        about changes in the schedule or in the plant.
    """
    
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
        
    def loadCommon(self, manager, config):
        """ Loads parameters that are common to all server implementations.
        
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
            config (ConfigParser): parameters that are common to all server implementations:
            - udpBroadcastPort (int): the port that is used by the broadcastqueue.
        Returns:
            True if all the parameters are successfully loaded.
        """
        try:
            #IPC using UDP sockets
            udpGroup = config.get("hieratika", "udpBroadcastQueueGroup")
            udpPort = config.getint("hieratika", "udpBroadcastQueuePort")
            self.streamUsers = manager.dict()
            self.udpQueue = BroacastQueue(udpGroup, udpPort)
        except (KeyError, ValueError, ConfigParser.Error) as e:
            log.critical("Failed to load configuration parameters {0}".format(e))
            return False
        return True

    def getTid(self):
        """
        Returns:
            A keyword which univocally identifies both the process and the thread.
        """
        tid = str(os.getpid())
        tid += "_"
        tid += str(threading.current_thread().ident) 
        return tid
 
    def streamData(self, username):
        """ Streams data back to the client using SSE.
            The inferface is provided by a broadcastqueue.
         
        Args:
            username (str): username of the user requesting for data to be streamed.
        """
        tid = None
        try:
            log.info("Streaming data for user {0}".format(username))
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
                        log.debug("Streaming {0}".format(encodedJson))
                        encodedPy = json.loads(encodedJson)
                        if ("logout" in encodedPy):
                            if (encodedPy["logout"] == username):
                                log.info("Stopping streamData as user {0} logged out".format(username))
                                break
                            else:
                                encodedJson = ""
                                time.sleep(0.01)
                        # Only trigger if the source was not from this tid. If it an update from 
                        # the plant, always trigger as some of the parameters might have failed to load
                        if ("scheduleUID" in encodedPy):
                            if (encodedPy["tid"] == tid):
                                encodedJson = ""
                yield "data: {0}\n\n".format(encodedJson)
        except Exception as e:
            log.critical("streamData failed {0}".format(e))
            self.streamData(username)
        log.info("Stopped streamData for user {0}".format(username))

    def queueStreamData(self, jSonData):
        """ Streams the input jSonData to all the SSE registered clients. This data contains the id of the client thread (received the first time the client registered in streamData), the scheduleUID related to the update and a dictionary with the list of variables that were update. If the update is from the plant the tid and scheduleUID parameters are ignored.
        
        Args 
            jSonData (json): the data to be streamed in the format {tid: threadIdWhichTriggeredTheUpdate, scheduleUID:idOfScheduleWhichTriggeredTheUpdate, variables:{varibleName1:variableValue1, ...}}
        """
        self.udpQueue.put(jSonData)

    def userLoggedIn(self, username):
        """ Called everytime a user is logged in into the system.
        Args:
            username (str): the username of the user.
        """
        pass

    def userLoggedOut(self, username):
        """ Called everytime a user is logged in into the system.
        Args:
            username (str): the username of the user.
        """
        self.udpQueue.put(json.dumps({"logout": username}))

    @abstractmethod
    def load(self, manager, config):
        """ Configures the server against a set of parameters. This set of parameters is specific for each server implementation.
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
            config(ConfigParser): the server specific implementation parameters are in the section "server-impl".
        Returns:
            True if the server is successfully configured.
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
           pageName (str): the page name to query.

       Returns:
           The Page or None if the name is not found.
        """
        pass

    @abstractmethod
    def getSchedule(self, scheduleUID):
        """ Gets the schedule associated to a given unique identifier.

        Args:
            scheduleUID (str): unique schedule identifier.
        Returns:
           The Schedule or None if the scheduleUID is not found.
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

