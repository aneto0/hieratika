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
import logging
import time
import uuid

##
# Project imports
##

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class ScriptoriumServer(object):
    """ TODO 
        TODO will have to decouple login management from parameter management. The same backend might be used in two places with different user authentication strategies.
    """
    
    __metaclass__ = ABCMeta

    def __init__(self):
        super().__init__()
        self.tokens = {}

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

    def getTokens(self):
        """
        Returns:
            The latest token table (dictionary of {tokenId: {user:username, lastInteraction: lastInteractionTime}})
        """
        return self.tokens

    def login(self, username):
        """ Tries to log a new user into the system.
            If successful a token will be associated to this user and registered into the system, so a subsequent call to
            isTokenValid, with this token, will return True.

        Returns:
            A User instance associated to a token described as a 32-character hexadecimal string or None if the login fails.
        """
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
           
        return user

    def logout(self, token):
        """ TODO 
        """
          asda 
        return user


    @abstractmethod
    def getUser(self, username):
        """ TODO
        """
        pass

    @abstractmethod
    def load(self, config):
        """ Configures the server.
            TODO
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
    def createSchedule(self, name, description, username, pageName):
        """ Creates a new schedule.
            TODO
        """
        pass

