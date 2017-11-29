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

        pagesFolder = config.get("hieratika", "pagesFolder")
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


#Gets all the pv information
@application.route("/getvariablesinfo", methods=["POST", "GET"])
def getplantinfo():
    log.debug("/getvariablesinfo")
    if (wserver.isTokenValid(request)):
        return wserver.getVariablesInfo(request)
    else:
        return "InvalidToken"
  
#Try to update the values in the plant
@application.route("/updateplant", methods=["POST", "GET"])
def updatePlant():
    log.debug("/updateplant")
    if (wserver.isTokenValid(request)):
        return wserver.updatePlant(request)
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
    
@application.route("/stream", methods=["POST", "GET"])
def stream():
    log.debug("/stream")
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
    return application.send_static_file("index.html")

@application.route("/pages/<filename>")
def pages(filename):
    return send_from_directory(wserver.getPagesFolder(), filename)

@application.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)

if __name__ == "__main__":
   
    #wserver.start()
    parser = argparse.ArgumentParser(description = "Flask http wserver for hieratika")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="Server port")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")
    parser.add_argument("-sm", "--serverModule", type=str, help="The server module implementation to be used (e.g. hieratika.servers.psps.pspsserver", required=True)
    parser.add_argument("-sc", "--serverClass", type=str, help="The server class implementation to be used (e.g. PSPSServer)", required=True)
    parser.add_argument("-am", "--authModule", type=str, default="hieratika.auths.stdaloneauth", help="The authentication module implementation to be used")
    parser.add_argument("-ac", "--authClass", type=str, default="HieratikaStdAloneAuth", help="The authentication class implementation to be used")
    parser.add_argument("-pf", "--pagesFolder", type=str, help="The location of the folder with the pages (e.g. ../../demo/server/psps/pages)", required=True)
    parser.add_argument("-sf", "--staticFolder", type=str, help="The location of the flask static folder (e.g. ../../clients/html5)", required=True)
    parser.add_argument("-ub", "--udpBroadcastQueueGroup", type=str, default="239.0.79.55", help="The udp multicast group for the broadcastqueue")
    parser.add_argument("-up", "--udpBroadcastQueuePort", type=int, default=23450, help="The udp multicast port for the broadcastqueue")
    parser.add_argument("-lr", "--loginMonitorUpdateRate", type=int, default=60,  help="How often should the login state should be checked (seconds) ")
    parser.add_argument("-lm", "--loginMonitorMaxInactivityTime", type=int, default=600,  help="Maximum time a user is allowed not to interact with the system before being logged out (seconds)")
    parser.add_argument("-lu", "--loginMaxUsers", type=int, default=4,  help="Maximum number of users that can be logged in at any time")
    parser.add_argument("-au", "--authImplOptions", type=str, nargs='+', help="Space separated list of options for the selected authetication module. Each option is colon separated (e.g. \"users:codac-dev-1;experts-1;experts-2,codac-dev-2;experts-1,codac-dev-3)\"", required=True)
    parser.add_argument("-si", "--serverImplOptions", type=str, nargs='+', help="Space separated list of options for the selected server implementation. Each option is colon separated (e.g. --serverImplOptions \"baseDir:../demo/server/psps\" numberOfLocks:8 maxXmlIds:8 maxXmlCachedTrees:16 defaultExperts:\"['experts-1','experts-2']\" standalone:False", required=True)

    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.add_section("hieratika")
    config.set("hieratika", "serverModule", args.serverModule)
    config.set("hieratika", "serverClass", args.serverClass)
    config.set("hieratika", "authModule", args.authModule)
    config.set("hieratika", "authClass", args.authClass)
    config.set("hieratika", "pagesFolder", args.pagesFolder)
    config.set("hieratika", "staticFolder", args.staticFolder)
    config.set("hieratika", "udpBroadcastQueueGroup", args.udpBroadcastQueueGroup)
    config.set("hieratika", "udpBroadcastQueuePort", args.udpBroadcastQueuePort)
    config.set("hieratika", "loginMonitorUpdateRate", args.loginMonitorUpdateRate)
    config.set("hieratika", "loginMonitorMaxInactivityTime", args.loginMonitorMaxInactivityTime)
    config.set("hieratika", "loginMaxUsers", args.loginMaxUsers)

    config.add_section("auth-impl")
    for option in args.authImplOptions:
        kv = option.split(":")
        if (len(kv) != 2):
            print "Bad formed option: {0}".format(option)
            exit()
        key = kv[0]
        value = kv[1]
        config.set("auth-impl", kv[0], kv[1])


    config.add_section("server-impl")
    for option in args.serverImplOptions:
        kv = option.split(":")
        if (len(kv) != 2):
            print "Bad formed option: {0}".format(option)
            exit()
        key = kv[0]
        value = kv[1]
        config.set("server-impl", kv[0], kv[1])


    print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    print "==============================================================================================================================="
    print "Flash HTTP server for Hieratika"
    print "==============================================================================================================================="
    print "The preferred way to start this service is with gunicorn:"
    print "gunicorn --preload --log-file=- -k gevent -w 16 -b 0.0.0.0:80 'hieratika.wservermain:start(config=\"PATH_TO_CONFIG.ini\")'"
    print "==============================================================================================================================="
   
    application = load(config) 
    if (application is not None):
        application.run(threaded=True, use_reloader = False, host=args.host, port=args.port)
