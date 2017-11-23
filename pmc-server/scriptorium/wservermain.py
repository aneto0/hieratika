#!/usr/bin/python

##
# Standard imports
##
import argparse
import logging
from flask import Flask, Response, request, send_from_directory

##
# Project imports
##
from scriptorium.wserver import WServer
from scriptorium.servers.psps.pspsserver import PSPSServer

#Logger configuration
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("{0}".format(__name__))

#Running a threaded Flask is ok only for debugging
#app.run(threaded=False, host=args.host, port=args.port)
#self.app.run(host='0.0.0.0')
#self.alive = False

            
pspsServer = PSPSServer()
config = {
    "baseDir": "demo",
    "numberOfLocks": 8,
    "usersXmlFilePath": "test/servers/psps/deploy/users.xml",
    "pagesXmlFilePath": "test/servers/psps/deploy/pages.xml"
}
if(pspsServer.load(config)):
    wserver = WServer(pspsServer, "../static", True)
    wserver.start()
    application = wserver.app

#Gets all the pv information
@application.route("/getvariablesinfo", methods=["POST", "GET"])
def getplantinfo():
    if (wserver.isTokenValid(request)):
        return wserver.getVariablesInfo(request)
    else:
        return "InvalidToken"
  
#Try to update the values in the plant
@application.route("/updateplant", methods=["POST", "GET"])
def updatePlant():
    if (wserver.isTokenValid(request)):
        return wserver.updatePlant(request)
    else:
        return "InvalidToken"
    
#Return the available schedules
@application.route("/getschedules", methods=["POST", "GET"])
def getschedules():
    if (wserver.isTokenValid(request)):
        return wserver.getSchedules(request) 
    else:
        return "InvalidToken"

#Return the available users
@application.route("/getusers", methods=["POST", "GET"])
def getusers():
    if (wserver.isTokenValid(request)):
        return wserver.getUsers(request) 
    else:
        return "InvalidToken"

#Return the available pages
@application.route("/getpages", methods=["POST", "GET"])
def getpages():
    if (wserver.isTokenValid(request)):
        return wserver.getPages(request) 
    else:
        return "InvalidToken"

#Returns the properties of a given page 
@application.route("/getpage", methods=["POST", "GET"])
def getpage():
    if (wserver.isTokenValid(request)):
        return wserver.getPage(request) 
    else:
        return "InvalidToken"

#Returns the properties of a given schedule
@application.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    if (wserver.isTokenValid(request)):
        return wserver.getSchedule(request)    
    else:
        return "InvalidToken"

#Returns the variables associated to a given schedule
@application.route("/getschedulevariablesvalues", methods=["POST", "GET"])
def getschedulevariablesValues():
    if (wserver.isTokenValid(request)):
        return wserver.getScheduleVariablesValues(request)
    else:
        return "InvalidToken"

#Tries to login a user
@application.route("/login", methods=["POST", "GET"])
def login():
    return wserver.login(request) 

#Logout a user
@application.route("/logout", methods=["POST", "GET"])
def logout():
    if (wserver.isTokenValid(request)):
        return wserver.logout(request) 
    else:
        return "InvalidToken"

#Updates a group of schedule variables
@application.route("/updateschedule", methods=["POST", "GET"])
def updateschedule():
    if (wserver.isTokenValid(request)):
        return wserver.updateSchedule(request)    
    else:
        return "InvalidToken"

#Commits a group of schedule variables
@application.route("/commitschedule", methods=["POST", "GET"])
def commitschedule():
    if (wserver.isTokenValid(request)):
        return wserver.commitSchedule(request)    
    else:
        return "InvalidToken"

#Creates a new schedule
@application.route("/createschedule", methods=["POST", "GET"])
def createschedule():
    if (wserver.isTokenValid(request)):
        return wserver.createSchedule(request)
    else:
        return "InvalidToken"
    
@application.route("/stream", methods=["POST", "GET"])
def stream():
    if (wserver.isTokenValid(request)):
        return Response(wserver.streamData(), mimetype="text/event-stream")
    else:
        return "InvalidToken"

@application.route("/")
def index():
    print "YEO"
    return wserver.app.send_static_file("index.html")

@application.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)


if __name__ == "__main__":
    #Start with gunicorn --preload -k gevent -w 16 -b 192.168.130.46:80 test
    
    #wserver.start()
    #parser = argparse.ArgumentParser(description = "Flask http wserver to prototype ideas for ITER level-1")
    #parser.add_argument("-H", "--host", vt="127.0.0.1", help="Server port")
    #parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    #args = parser.parse_args()
    wserver.info()    
