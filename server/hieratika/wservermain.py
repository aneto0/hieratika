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
import ast
import ConfigParser
import importlib
import logging
import multiprocessing
import os
from flask import Flask, Response, request, send_from_directory

##
# Project imports
##
from hieratika.wserver import WServer
from hieratika.wtransformation import WTransformation

##
# Logger configuration
##
#TODO change to fileConfig (see https://docs.python.org/2/howto/logging.html). This can be input to gunicorn using --log-config (TBC)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##

# The Flask application
application = Flask(__name__, static_url_path="")

# The WServer implementation
wserver = WServer()

# The WTransformation implementation
wtransformation = WTransformation()

def load(config):
    try:
        serverModuleName = config.get("hieratika", "serverModule")
        log.info("Server module is {0}".format(serverModuleName))
        serverModule = importlib.import_module(serverModuleName)

        serverClassName = config.get("hieratika", "serverClass")
        log.info("Server class is {0}".format(serverClassName))
        serverClass = getattr(serverModule, serverClassName)

        authModuleName = config.get("hieratika", "authModule")
        log.info("Auth module is {0}".format(authModuleName))
        authModule = importlib.import_module(authModuleName)

        authClassName = config.get("hieratika", "authClass")
        log.info("Auth class is {0}".format(authClassName))
        authClass = getattr(authModule, authClassName)

        transformationModuleNames = []
        transformationClassNames = []
        if (config.has_option("hieratika", "transformationModules")):
            transformationModuleNames = config.get("hieratika", "transformationModules")
            log.info("Transformation modules are {0}".format(transformationModuleNames))
            transformationModuleNames = ast.literal_eval(transformationModuleNames)

            transformationClassNames = config.get("hieratika", "transformationClasses")
            log.info("Transformation classes are {0}".format(transformationClassNames))
            transformationClassNames = ast.literal_eval(transformationClassNames)

        pagesFolder = config.get("hieratika", "pagesFolder")
        #Translate into absolute path so that it can be used by other modules (which belong to other directories) as well.
        pagesFolder = os.path.abspath(pagesFolder)
        config.set("hieratika", "pagesFolder", pagesFolder)
        application.static_folder = config.get("hieratika", "staticFolder")
        application.debug = True
        application.logger.setLevel(logging.DEBUG)
        server = serverClass()
        auth = authClass()

        manager = multiprocessing.Manager()
        log.info("Loading server common configuration")
        ok = server.loadCommon(manager, config)
        if (ok):
            log.info("Loading server configuration")
            ok = server.load(manager, config)
        else:
            log.critical("Failed to load common server configuration")
        if (ok):
            log.info("Loading auth configuration")
            ok = auth.loadCommon(manager, config)
        else:
            log.critical("Failed to load server configuration")
        if (ok):
            ok = auth.load(manager, config)
        if (ok):
            auth.addLogListener(server)
            ok = auth.start()
        else:
            log.critical("Failed to load auth configuration")

        transformations = []
        if (ok):
            for transformationModuleName, transformationClassName in zip(transformationModuleNames, transformationClassNames):
                transformationModule = importlib.import_module(transformationModuleName) 
                transformationClass = getattr(transformationModule, transformationClassName)
                transformationInstance = transformationClass()
                transformations.append(transformationInstance)
                log.info("Loading transformation {0}.{1} common configuration".format(transformationModuleName, transformationClassName))
                ok = transformationInstance.loadCommon(manager, config)
                if (ok):
                    log.info("Loading transformation {0}.{1} configuration".format(transformationModuleName, transformationClassName))
                    ok = transformationInstance.load(manager, config)
                else:
                    log.info("Failed Loading transformation {0}.{1} common configuration".format(transformationModuleName, transformationClassName))

                if (ok):
                    transformationInstance.setServer(server)
                else:
                    log.info("Failed Loading transformation {0}.{1} configuration".format(transformationModuleName, transformationClassName))
                    break

        if (ok):
            wtransformation.setTransformations(transformations)

        if (ok):
            #The web app which is a Flask standard application
            wserver.setServer(server)
            wserver.setAuth(auth)
            wserver.setPagesFolder(pagesFolder)
            return application
        else:
            log.critical("Failed to load either the server or the auth service") 
    except (KeyError, ValueError, ConfigParser.Error) as e:
        #Trap both IOError 
        log.critical("Failed to load configuration: {0}".format(e))
        exit()

def start(*args, **kwargs):
    configFilePath = kwargs["config"]
    try:
        with open(configFilePath, "r") as configFile:
            config = ConfigParser.ConfigParser()
            config.readfp(configFile)
            return load(config)
    except (IOError, ConfigParser.Error) as e:
        #Trap both IOError 
        log.critical("Failed to load configuration file {0} : {1}".format(configFile, e))
        exit()

#Gets all the variables information for a given configuration
@application.route("/getvariablesinfo", methods=["POST", "GET"])
def getplantinfo():
    log.debug("/getvariablesinfo")
    if (wserver.isTokenValid(request)):
        return wserver.getVariablesInfo(request)
    else:
        return "InvalidToken"
  
#Gets all the variables information for a given library
@application.route("/getlibraryvariablesinfo", methods=["POST", "GET"])
def getlibraryvariablesinfo():
    log.debug("/getlibraryvariablesinfo")
    if (wserver.isTokenValid(request)):
        return wserver.getLibraryVariablesInfo(request)
    else:
        return "InvalidToken"

#Gets all the available transformations
@application.route("/gettransformationsinfo", methods=["POST", "GET"])
def gettransformationsinfo():
    log.debug("/gettransformationsinfo")
    if (wserver.isTokenValid(request)):
        return wserver.getTransformationsInfo(request)
    else:
        return "InvalidToken"

#Try to update the values in the plant
@application.route("/updateplant", methods=["POST", "GET"])
def updateplant():
    log.debug("/updateplant")
    if (wserver.isTokenValid(request)):
        return wserver.updatePlant(request)
    else:
        return "InvalidToken"

#Return the available libraries (for a given user and a given library type)
@application.route("/getlibraries", methods=["POST", "GET"])
def getlibraries():
    log.debug("/getlibraries")
    if (wserver.isTokenValid(request)):
        return wserver.getLibraries(request) 
    else:
        return "InvalidToken"

#Saves/creates a library with new values
@application.route("/savelibrary", methods=["POST", "GET"])
def savelibrary():
    log.debug("/savelibrary")
    if (wserver.isTokenValid(request)):
        return wserver.saveLibrary(request) 
    else:
        return "InvalidToken"

    
#Return the available schedules
@application.route("/getschedules", methods=["POST", "GET"])
def getschedules():
    log.debug("/getschedules")
    if (wserver.isTokenValid(request)):
        return wserver.getSchedules(request) 
    else:
        return "InvalidToken"

#Return the available users
@application.route("/getusers", methods=["POST", "GET"])
def getusers():
    log.debug("/getusers")
    if (wserver.isTokenValid(request)):
        return wserver.getUsers(request) 
    else:
        return "InvalidToken"

#Returns the information about a given user
@application.route("/getuser", methods=["POST", "GET"])
def getuser():
    log.debug("/getuser")
    if (wserver.isTokenValid(request)):
        return wserver.getUser(request) 
    else:
        return "InvalidToken"


#Return the available pages
@application.route("/getpages", methods=["POST", "GET"])
def getpages():
    log.debug("/getpages")
    if (wserver.isTokenValid(request)):
        return wserver.getPages(request) 
    else:
        return "InvalidToken"

#Returns the properties of a given page 
@application.route("/getpage", methods=["POST", "GET"])
def getpage():
    log.debug("/getpage")
    if (wserver.isTokenValid(request)):
        return wserver.getPage(request) 
    else:
        return "InvalidToken"

#Returns the properties of a given schedule
@application.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    log.debug("/getschedule")
    if (wserver.isTokenValid(request)):
        return wserver.getSchedule(request)    
    else:
        return "InvalidToken"

#Returns the variables associated to a given schedule
@application.route("/getschedulevariablesvalues", methods=["POST", "GET"])
def getschedulevariablesValues():
    log.debug("/getschedulevariablesvalues")
    if (wserver.isTokenValid(request)):
        return wserver.getScheduleVariablesValues(request)
    else:
        return "InvalidToken"

#Returns the variables associated to a given library (identified by its uid)
@application.route("/getlibraryvariablesvalues", methods=["POST", "GET"])
def getlibraryvariablesvalues():
    log.debug("/getlibraryvariablesvalues")
    if (wserver.isTokenValid(request)):
        return wserver.getLibraryVariablesValues(request)
    else:
        return "InvalidToken"

#Tries to login a user
@application.route("/login", methods=["POST", "GET"])
def login():
    log.debug("/login")
    return wserver.login(request) 

#Logout a user
@application.route("/logout", methods=["POST", "GET"])
def logout():
    log.debug("/logout")
    if (wserver.isTokenValid(request)):
        wserver.logout(request) 
        return ""
    else:
        return "InvalidToken"

#Updates a group of schedule variables
@application.route("/updateschedule", methods=["POST", "GET"])
def updateschedule():
    log.debug("/updateschedule")
    if (wserver.isTokenValid(request)):
        return wserver.updateSchedule(request)    
    else:
        return "InvalidToken"

#Commits a group of schedule variables
@application.route("/commitschedule", methods=["POST", "GET"])
def commitschedule():
    log.debug("/commitschedule")
    if (wserver.isTokenValid(request)):
        return wserver.commitSchedule(request)    
    else:
        return "InvalidToken"

#Creates a new schedule
@application.route("/createschedule", methods=["POST", "GET"])
def createschedule():
    log.debug("/createschedule")
    if (wserver.isTokenValid(request)):
        return wserver.createSchedule(request)
    else:
        return "InvalidToken"

#Applies a transformation
@application.route("/transform", methods=["POST", "GET"])
def transform():
    log.debug("/transform")
    if (wserver.isTokenValid(request)):
        return wtransformation.transform(request)
    else:
        return "InvalidToken"
    
@application.route("/stream", methods=["POST", "GET"])
def stream():
    log.debug("/stream")
    if (wserver.getServer().isStandalone()):
        log.critical("No streaming supported in a standalone implementation")
        return "NotAvailable"
    else:
        if (wserver.isTokenValid(request)):
            if (request.method == "POST"):
                tokenId = request.form["token"]
            else:
                tokenId = request.args["token"]

            username = wserver.getAuth().getUsernameFromToken(tokenId)
            if (username is not None): 
                #Note that this cannot be interfaced through the wserver (otherwise the yield reply will not work properly)
                return Response(wserver.getServer().streamData(username), mimetype="text/event-stream")
        else:
            return "InvalidToken"

@application.route("/")
def index():
    log.debug("/")
    if (wserver.getServer().isStandalone()):
        return application.send_static_file("index-standalone.html")
    else:
        return application.send_static_file("index.html")

@application.route("/pages/<filename>")
def pages(filename):
    return send_from_directory(wserver.getPagesFolder(), filename)

@application.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('../../tmp', filename)

if __name__ == "__main__":
   
    #wserver.start()
    parser = argparse.ArgumentParser(description = "Flask http wserver for hieratika")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="Server port")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")
    parser.add_argument("-i", "--ini", type=str, help="The location of the ini file", required=True)
    args = parser.parse_args()

    print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    print "==============================================================================================================================="
    print "Flash HTTP server for Hieratika"
    print "==============================================================================================================================="
    print "The preferred way to start this service is with gunicorn:"
    print "gunicorn --preload --log-file=- -k gevent -w 16 -b 0.0.0.0:80 'hieratika.wservermain:start(config=\"PATH_TO_CONFIG.ini\")'"
    print "==============================================================================================================================="
   
    try:
        with open(args.ini, "r") as configFile:
            config = ConfigParser.ConfigParser()
            config.readfp(configFile)
            application = load(config) 
            if (application is not None):
                application.run(threaded=True, use_reloader = False, host=args.host, port=args.port)
    except (IOError, ConfigParser.Error) as e:
        #Trap both IOError 
        log.critical("Failed to load configuration file {0} : {1}".format(configFile, e))
        exit()

