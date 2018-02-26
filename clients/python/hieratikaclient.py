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
__date__ = "23/02/2018"

##
# Standard imports
##
import httplib
import json
import logging
import urllib

##
# Project imports
##
from hieratika.hconstants import HieratikaConstants
from hieratika.schedule import Schedule
from hieratika.schedulefolder import ScheduleFolder
from hieratika.user import User

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

class HieratikaClient (object):
    """ A python interface to Hieratika using HTTP.
        Note that the login function shall be called before any further communication with the server is performed.
    """
    
    def __init__(self, baseURL):
        """ Constructor. 
        
        Args:
            baseURL (str): the URL where the Hieratika server is running on.            
        """
        self.baseURL = baseURL
        self.headers = {"Content-type": "application/x-www-form-urlencoded"}
        self.user = None
        self.conn = None
        
    def login(self, username, password):
        """ Logins in a user to Hieratika.
        
        Args:
            username (str): the username of the Hieratika user that is going to be used for all the RPC calls.
            password (str): the password of the user defined above.
        Returns:
            True if the user was successfully logged in.
        """

        self.conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        params = urllib.urlencode({"username": username, "password": password})
        self.conn.request("POST", "login", params, self.headers)
        response = self.conn.getresponse()
        ret = False
        self.user = None
        if (response.status == 200):
            userDict = json.loads(response.read())
            self.user = User.fromSerializableDict(userDict)
            ret = True
            log.info("Logged in user {0}".format(username))
        else:
            log.critical("Could not login user {0}".format(username))
            
        return ret

    def logout(self):
        """ Logs out the currently logged in user from the system.
        """
        if ((self.conn is not None) and (self.user is not None)):
            params = urllib.urlencode({"token": self.user.getToken()})
            self.conn.request("POST", "logout", params, self.headers)
            response = self.conn.getresponse()
            if (response.status == 200):
                log.info("Logged out user {0}".format(self.user.getUsername()))
            else:
                log.info("Could not logout user {0}".format(self.user.getUsername()))

    def getSchedules(self, username, pageName, parentFolders):
        """ Gets all the schedules that are avaiable for a given user in a given page.

        Args:
           username (str): the username to which the returned schedules belong to. 
           pageName (str): the name of the page associated to the schedule.
           parentFolders ([str]): list of the parent folders of the folders to be retrieved.
        Returns:
            An array with all the schedules that are available for the requested user in the 
            specified page.
        """
        schedules = []
        if ((self.conn is not None) and (self.user is not None)):
            params = urllib.urlencode({"token": self.user.getToken(), "pageName": pageName, "username": username, "parentFolders": json.dumps(parentFolders)})
            self.conn.request("POST", "getschedules", params, self.headers)
            response = self.conn.getresponse()
            if (response.status == 200):
                serverReply = response.read()
                if (serverReply != HieratikaConstants.INVALID_PARAMETERS):
                    schedulesDict = json.loads(serverReply)
                    for s in schedulesDict:
                        schedules.append(Schedule.fromSerializableDict(s))
                    log.info("Retrieved {0} schedules for user {1} in page {2}".format(len(schedules), username, pageName))
            else:
                log.info("Could not get the schedules for {0} {1} {2}".format(username, pageName, parentFolders))
        return schedules

    def getScheduleFolders(self, username, pageName, parentFolders):
        """ Gets all the schedule folders that are avaiable for a given user in a given page.

        Args:
           username (str): the username to which the returned schedules belong to. 
           pageName (str): the name of the page associated to the schedule.
           parentFolders ([str]): list of the parent folders of the folders to be retrieved.
        Returns:
            An array with all the ScheduleFolders that are available for the requested user in the 
            specified page.
        """
        scheduleFolders = []
        if ((self.conn is not None) and (self.user is not None)):
            params = urllib.urlencode({"token": self.user.getToken(), "pageName": pageName, "username": username, "parentFolders": json.dumps(parentFolders)})
            self.conn.request("POST", "getschedulefolders", params, self.headers)
            response = self.conn.getresponse()
            if (response.status == 200):
                serverReply = response.read()
                if (serverReply != HieratikaConstants.INVALID_PARAMETERS):
                    scheduleFoldersDict = json.loads(serverReply)
                    for s in scheduleFoldersDict:
                        scheduleFolders.append(ScheduleFolder.fromSerializableDict(s))
                    log.info("Retrieved {0} schedule folders for user {1} in page {2}".format(len(scheduleFolders), username, pageName))
            else:
                log.info("Could not get the schedules for {0} {1} {2}".format(username, pageName, parentFolders))
        return scheduleFolders

    def updatePlantFromSchedule(self, pageName, scheduleUID):
        """ Updates the values of the plant from a given schedule.

        Args:
            pageName (str): the name of the page associated to the schedule.
            scheduleUID (str): the unique identifier of the schedule to be set against the plant.
        Returns:
            True if the values are successfully updated.
        """
        toReturn = False
        if ((self.conn is not None) and (self.user is not None)):
            params = urllib.urlencode({"token": self.user.getToken(), "pageName": pageName, "scheduleUID": scheduleUID, "tid": "0"})
            self.conn.request("POST", "updateplantfromschedule", params, self.headers)
            response = self.conn.getresponse()
            if (response.status == 200):
                toReturn = (response.read() == HieratikaConstants.OK)
        return toReturn
        
    def loadIntoPlant(self, pageName):
        """ Loads the specified page into the plant.

        Args:
            pageName (str): the name of the page associated to the schedule.
        Returns:
            True if all the parameters were successfully loaded.
        """
        toReturn = False
        if ((self.conn is not None) and (self.user is not None)):
            params = urllib.urlencode({"token": self.user.getToken(), "pageNames": json.dumps([pageName])})
            self.conn.request("POST", "loadintoplant", params, self.headers)
            response = self.conn.getresponse()
            if (response.status == 200):
                toReturn = (response.read() == HieratikaConstants.OK)
        return toReturn

    def getUser(self):
        """
        Returns:
            The currently logged in user.
        """
        return self.user
