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
import httplib
import json
import logging
import multiprocessing
import time
import unittest
import urllib

##
# Project imports
##

##
# Logger configuration
##
#TODO change to fileConfig (see https://docs.python.org/2/howto/logging.html). This can be input to gunicorn using --log-config (TBC)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("{0}".format(__name__))


##
# Class definition
##
class TestHTTP(unittest.TestCase):

    def setUp(self):
        self.baseURL = "127.0.0.1:7000"
        self.testPage = "DemoTypes"

        params = urllib.urlencode({"username": "codac-dev-1", "password": ""})
        self.headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        conn.request("POST", "login", params, self.headers)
        response = conn.getresponse()
        if (response.status == 200):
            user = json.loads(response.read())
            try:
                self.token = user["token"]
            except KeyError as e:
                log.critical(e)

    def tearDown(self):
        params = urllib.urlencode({"token": self.token})
        conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        conn.request("POST", "logout", params, self.headers)

    def test_login(self):
        self.assertTrue(len(self.token) > 0)

    def test_getpages(self):
        params = urllib.urlencode({"token": self.token})
        conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        conn.request("POST", "getpages", params, self.headers)
        response = conn.getresponse()
        if (response.status == 200):
            pages = json.loads(response.read())
            self.assertTrue(len(pages) > 0)
        else:
            self.assertTrue(False)

    def test_getvariablesinfo(self):
        variables = ["DT@BT@DBL", "DT@BT@DBL2", "DT@LB@LIB1", "DT@LB@LIB2", "DT@BT@DBLA", "DT@BT@DBLM", "DT"]
        params = urllib.urlencode({"token": self.token, "pageName": self.testPage, "variables": json.dumps(variables)})
        conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        conn.request("POST", "getvariablesinfo", params, self.headers)
        response = conn.getresponse()
        if (response.status == 200):
            variables = json.loads(response.read())
            self.assertTrue(len(variables) > 0)
        else:
            self.assertTrue(False)

    def test_getlibraryvariablesinfo(self):
        variables = ["AA@BB@CC", "AA@BB@DD"]
        params = urllib.urlencode({"token": self.token, "libraryType": "testlib1", "variables": json.dumps(variables)})
        conn = httplib.HTTPConnection("{0}".format(self.baseURL))
        conn.request("POST", "getlibraryvariablesinfo", params, self.headers)
        response = conn.getresponse()
        if (response.status == 200):
            variables = json.loads(response.read())
            self.assertTrue(len(variables) > 0)
        else:
            self.assertTrue(False)


    def test_full_page_load(self):
        self.test_getvariablesinfo()
        self.test_getlibraryvariablesinfo()
        self.test_getlibraryvariablesinfo()
        self.test_getlibraryvariablesinfo()
        self.assertTrue(True)
    
    def test_full_page_load_MP_CB(self):
        nRepeats = 3
        time.sleep(0.1)
        for i in range(nRepeats):
            self.test_full_page_load()
            time.sleep(0.1)
        self.assertTrue(True)

    def test_full_page_load_MP(self):
        procs = []
        nProcs = 2
        for i in range(nProcs):
            procs.append(multiprocessing.Process(target = self.test_full_page_load_MP_CB))

        for p in procs:
            p.start() 

        for p in procs:
            p.join() 

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
