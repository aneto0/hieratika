import httplib
import json
import logging
import multiprocessing
import time
import unittest
import urllib

from flask import request

from scriptorium.wserver import WServer
from scriptorium.servers.psps.pspsserver import PSPSServer

logging.basicConfig(level=logging.DEBUG)

class TestRequest:
    def __init__(self, form):
        self.form = form

class TestWServer(unittest.TestCase):

    def setUp(self):
        pspsServer = PSPSServer()
        config = {
            "baseDir": "test/servers/psps/deploy",
            "numberOfLocks": 8,
            "usersXmlFilePath": "test/servers/psps/users.xml",
            "pagesXmlFilePath": "test/servers/psps/pages.xml"
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

    def test_getPlantInfo(self):
        variables = ["AA@AA@AA@AA@AA", "AA@AA@AA@AA@BB", "AA@AA@AA@AA@CC", "AA@AA@AA@BB@AA", "AA@AA@AA@BB@BB", "AA@AA@AA@BB@CC", "BB@AA@AA@AA@AA", "BB@AA@AA@AA@BB", "BB@AA@AA@AA@CC", "BB@AA@AA@BB@AA", "BB@AA@AA@BB@BB", "BB@AA@AA@BB@CC"]
        request = TestRequest({"token": self.token, "pageName": "test0", "variables": json.dumps(variables)})
        variablesInfo = json.loads(self.wserver.getPlantInfo(request))
        for i, variableInfo in enumerate(variablesInfo):
            #TODO finish for all the other properties or implement method eq in future variable class
            self.assertEqual(variables[i], variableInfo["name"])

    def test_getSchedules(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = self.wserver.getSchedules(request)
        self.assertNotEqual(schedules, None)
        #TODO finish asserts

    def test_getScheduleVariablesValues(self):
        request = TestRequest({"token": self.token, "pageName": "test0", "username": "codac-dev-1"})
        schedules = json.loads(self.wserver.getSchedules(request))
        request = TestRequest({"token": self.token, "scheduleUID": schedules[0]["uid"]})
        schedules = self.wserver.getScheduleVariablesValues(request)
        self.assertNotEqual(schedules, None)
        print schedules

       
if __name__ == '__main__':
    unittest.main()

