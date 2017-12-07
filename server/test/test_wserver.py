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
import ConfigParser
import importlib
import json
import logging
import multiprocessing
import os
import time
import unittest

##
# Project imports
##
from hieratika.wserver import WServer
from hieratika.servers.psps.pspsserver import PSPSServer

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

##
# Class definition
##
class TestRequest:
    def __init__(self, form):
        self.form = form

class TestWServer(unittest.TestCase):

    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.add_section("hieratika")
        config.set("hieratika", "structSeparator", "@")
        config.set("hieratika", "standalone", "False")
        config.set("hieratika", "pagesFolder", "test/servers/psps/deploy/pages")
        config.set("hieratika", "serverModule", "hieratika.servers.psps.pspsserver")
        config.set("hieratika", "serverClass", "PSPSServer")
        config.set("hieratika", "udpBroadcastQueueGroup", "239.0.79.55")
        config.set("hieratika", "udpBroadcastQueuePort", "23450")
        config.set("hieratika", "authModule", "hieratika.auths.basicauth")
        config.set("hieratika", "authClass", "HieratikaBasicAuth")
        config.set("hieratika", "loginMonitorUpdateRate", "60")
        config.set("hieratika", "loginMonitorMaxInactivityTime", 600)
        config.set("hieratika", "loginMaxUsers", 4)

        config.add_section("server-impl")
        config.set("server-impl", "baseDir", "test/servers/psps/deploy")
        config.set("server-impl", "numberOfLocks", 8)
        config.set("server-impl", "maxXmlIds", 32)
        config.set("server-impl", "maxXmlCachedTrees", 16)
        config.set("server-impl", "defaultExperts", "['experts-1', 'experts-2']")
        config.set("server-impl", "autoCreatePages", "True")

        config.add_section("auth-impl")
        config.set("auth-impl", "users", "codac-dev-1;experts-1;experts-2,codac-dev-2;experts-1,codac-dev-3")

        serverModuleName = config.get("hieratika", "serverModule")
        serverModule = importlib.import_module(serverModuleName)

        serverClassName = config.get("hieratika", "serverClass")
        serverClass = getattr(serverModule, serverClassName)

        authModuleName = config.get("hieratika", "authModule")
        authModule = importlib.import_module(authModuleName)

        authClassName = config.get("hieratika", "authClass")
        authClass = getattr(authModule, authClassName)

        pagesFolder = config.get("hieratika", "pagesFolder")
        #Translate into absolute path so that it can be used by other modules (which belong to other directories) as well.
        pagesFolder = os.path.abspath(pagesFolder)
        config.set("hieratika", "pagesFolder", pagesFolder)
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
            self.wserver = WServer()
            self.wserver.setServer(server)
            self.wserver.setAuth(auth)
            self.wserver.setPagesFolder(pagesFolder)
       
        if (ok): 
            request = TestRequest({"username": "codac-dev-1", "password": ""})
            user = self.wserver.login(request)
            user = json.loads(user)
            self.token = user["token"]

    def test_login(self):
        request = TestRequest({"username": "codac-dev-1", "password" : ""})
        user = self.wserver.login(request)
        self.assertNotEqual(user, None)
        user = json.loads(user)
        try:
            self.assertEqual(user["username"], "codac-dev-1")
            self.assertNotEqual(len(user["token"]), 0)
        except KeyError as e:
            log.critical(e)
            self.assertTrue(False)

    def test_getVariablesInfo(self):
        variables = ["AA", "BB", "AA@AA@AA@AA@AA", "BB@AA@AA@BB@CC"]
#, "AA@AA", "AA@AA@AA@AA", "BB", "BB@AA", "BB@AA@AA", "AA@AA@AA@AA@AA", "AA@AA@AA@AA@BB", "AA@AA@AA@AA@CC", "AA@AA@AA@BB@AA", "AA@AA@AA@BB@BB", "AA@AA@AA@BB@CC", "BB@AA@AA@AA@AA", "BB@AA@AA@AA@BB", "BB@AA@AA@AA@CC", "BB@AA@AA@BB@AA", "BB@AA@AA@BB@BB", "BB@AA@AA@BB@CC"]
        request = TestRequest({"token": self.token, "pageName": "test0", "variables": json.dumps(variables)})
        jsonReply = self.wserver.getVariablesInfo(request)
        variablesInfo = json.loads(jsonReply)
        print variablesInfo
        for i, variableInfo in enumerate(variablesInfo):
            #TODO finish for all the other properties or implement method eq in future variable class
            #self.assertEqual(variables[i], variableInfo["name"])
            print json.dumps(variableInfo, indent=4, sort_keys=True)
            #varAAAAAAAAAA = variableInfo["AA"]["AA"]["AA"]["AA"]
            #varAAAAAAAABB = variableInfo["AA"]["AA"]["AA"]["BB"]
            #varAAAAAABBAA = variableInfo["AA"]["AA"]["BB"]["AA"]
            #print json.dumps(varAAAAAAAAAA, indent=4, sort_keys=True)
            #print json.dumps(varAAAAAAAABB, indent=4, sort_keys=True)
            #print json.dumps(varAAAAAABBAA, indent=4, sort_keys=True)

    def test_commitSchedule(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = json.loads(self.wserver.getSchedules(request))
        request = TestRequest({"token": self.token, "scheduleUID": schedules[0]["uid"], "tid": "", "variables":json.dumps({"AA@AA@AA@AA@AA": 7})})
        ok = self.wserver.commitSchedule(request)
        self.assertEqual(ok, "ok")

    def test_updateSchedule(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = json.loads(self.wserver.getSchedules(request))
        request = TestRequest({"token": self.token, "scheduleUID": schedules[0]["uid"], "tid": "", "variables":json.dumps({"AA@AA@AA@AA@AA": 4})})
        ok = self.wserver.updateSchedule(request)
        self.assertEqual(ok, "ok")

    def test_updatePlant(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "tid": "", "variables":json.dumps({"AA@AA@AA@AA@AA": 4})})
        ok = self.wserver.updatePlant(request)
        self.assertEqual(ok, "ok")

    def test_getSchedules(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = self.wserver.getSchedules(request)
        self.assertNotEqual(schedules, None)
        #TODO finish asserts

    def test_getLibraries(self):
        request = TestRequest({"token": self.token, "type": "testtype1", "username": "codac-dev-1"})
        libraries = self.wserver.getLibraries(request)
        self.assertNotEqual(libraries, None)
        #TODO finish asserts

    def test_getScheduleVariablesValues(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = json.loads(self.wserver.getSchedules(request))
        request = TestRequest({"token": self.token, "scheduleUID": schedules[0]["uid"]})
        variablesValues = self.wserver.getScheduleVariablesValues(request)
        self.assertNotEqual(variablesValues, None)

    def test_getLibraryVariablesValues(self):
        request = TestRequest({"token": self.token, "type": "testtype1", "username": "codac-dev-1"})
        libraries = json.loads(self.wserver.getLibraries(request))
        request = TestRequest({"token": self.token, "libraryUID": libraries[0]["uid"]})
        variablesValues = self.wserver.getLibraryVariablesValues(request)
        self.assertNotEqual(libraries, None)
        #TODO finish asserts

       
if __name__ == '__main__':
    unittest.main()

