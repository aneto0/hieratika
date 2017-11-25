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
import json
import logging
import time
import unittest

##
# Project imports
##
from scriptorium.wserver import WServer
from scriptorium.servers.psps.pspsserver import PSPSServer

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
        pspsServer = PSPSServer()
        config = {
            "baseDir": "test/servers/psps/deploy",
            "numberOfLocks": 8,
            "usersXmlFilePath": "test/servers/psps/deploy/users.xml",
            "pagesXmlFilePath": "test/servers/psps/deploy/pages.xml"
        }
        pspsServer.load(config)
        self.wserver = WServer(pspsServer, "../static", True)
        request = TestRequest({"username": "codac-dev-1"})
        user = self.wserver.login(request)
        user = json.loads(user)
        self.token = user["token"]

    def test_login(self):
        request = TestRequest({"username": "codac-dev-1"})
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

    def test_getScheduleVariablesValues(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = json.loads(self.wserver.getSchedules(request))
        request = TestRequest({"token": self.token, "scheduleUID": schedules[0]["uid"]})
        variablesValues = self.wserver.getScheduleVariablesValues(request)
        self.assertNotEqual(variablesValues, None)

       
if __name__ == '__main__':
    unittest.main()

