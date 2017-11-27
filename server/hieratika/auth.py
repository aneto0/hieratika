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
__date__ = "27/11/2017"

##
# Standard imports
##
from abc import ABCMeta, abstractmethod
import ConfigParser
import datetime
import logging
import multiprocessing
import os
import time
import threading
import uuid

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class HieratikaAuth(object):
    """ TODO 
    """
    
    __metaclass__ = ABCMeta

    def __init__(self):
        self.logListeners = []

    def addLogListener(self, listener):
        """ Registers a listener which will be notfied everytime a user logs in or out from the system.
            The listener class shall implement the functions userLoggedIn(username) and userLoggedOut(username).
        Args(listener):
            The object to notify everytime a user logs in or out from the system.
        """
        self.logListeners.append(listener)

    def loadCommon(self, manager, config):
        """ Loads parameters that are common to all authentication implementations.
        
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
            config (ConfigParser): parameters that are common to all authenticate implementations:
            - loginMonitorUpdateRate (int): the time interval in seconds at which the state of logged in users is to be checked. 
            - loginMonitorMaxInactivityTime (int): maximum time that a given user can stay logged in without interacting with the server.
            - loginMaxUsers (int): maximum number of users that can be logged in at any time.
        Returns:
            True if all the parameters are successfully loaded.
        """
        try:
            self.tokens = manager.dict()
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

    def start(self):
        """ Starts the login monitoring thread.
        """
        #To force the killing of the threadCleaner thread with Ctrl+C
        log.info("Starting login monitoring thread")
        self.loginMonitorThread.daemon = True
        self.loginMonitorThread.start()
        return True

    def stop(self):
        """ Stops the login monitoring thread.
        """
        log.info("Stopping login monitoring thread")
        self.loginMonitorEvent.set()
        self.loginMonitorThread.join()
        log.info("Stopped login monitoring thread")
        return True

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

    def login(self, username, password):
        """ Tries to log a new user into the system.
            If successful a token will be associated to this user and registered into the system, so a subsequent call to
            isTokenValid, with this token, will return True.

        Returns:
            A User instance associated to a token described as a 32-character hexadecimal string or None if the login fails.
        """
        numberOfLoggedUsers = len(self.tokens)
        ok = (numberOfLoggedUsers < self.loginMaxUsers)
        if (ok):
            ok = self.authenticate(username, password)
            user = None
            if (ok):
                user = self.getUser(username) 
                ok = (user is not None)
            if (ok):
                log.info("{0} logged in successfully".format(username))
                loginToken = uuid.uuid4().hex
                self.tokens[loginToken] = {"user": username, "lastInteraction": int(time.time())}
                user.setToken(loginToken)
                for l in self.logListeners:
                    l.userLoggedIn(username)
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
        info = "Server information\n"
        info = info + "Logged users\n"
        info = info + "{0:40}|{1:40}\n".format("user", "Last interaction")
        keys = self.tokens.keys()
        for k in keys:
            user = self.tokens[k]["user"]
            interactionTime = str(datetime.datetime.fromtimestamp(self.tokens[k]["lastInteraction"]))
            info = info + "{0:40}|{1:40}\n".format(user, interactionTime)
        log.info(info)


    def logout(self, token):
        """ Logsout the user identified with the given token from the system.

        Args:
            token (str): token that was provided to the user when was logged in
        """
        try:
            user = self.tokens[token]["user"]
            log.info("Logging out {0} with token {1}".format(user, token))
            del(self.tokens[token])
            for l in self.logListeners:
                l.userLoggedOut(user)
        except KeyError as e:
            log.critical("Failed to logout user with token {0} : {1}".format(token, e))

    @abstractmethod
    def load(self, manager, config):
        """ Configures the authentication service against a set of parameters. This set of parameters is specific for each implementation.
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
            config(ConfigParser): the authentication specific implementation parameters are in the "auth-impl" section.
        Returns:
            True if the authentication service is successfully configured.
        """
        pass

    @abstractmethod 
    def authenticate(self, username, password):
        """ Authenticates a user into the system.
        Args:
            username (str): the username.
            password (str): the user password.
        Returns:
            True if the user is successfully authenticated.
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
    def getUser(self, username):
        """ 
        Args:
            username(str): the username of the user to get.
        Returns:
            The user associated to the given username or None if not found.
        """
        pass

