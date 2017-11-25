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
import logging
import time
import unittest

##
# Project imports
##
from scriptorium.servers.psps.pspsserver import PSPSServer

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))
logging.basicConfig(level=logging.DEBUG)

##
# Class definition
##
class TestPSPSServer(unittest.TestCase):

    def setUp(self):
        pass

    def test_constructor(self):
        pspsServer = PSPSServer()
        self.assertTrue(True)

    def test_load(self):
        pspsServer = PSPSServer()
        config = {
            "baseDir": "test/servers/psps/deploy",
            "numberOfLocks": 8,
            "usersXmlFilePath": "test/servers/psps/deploy/users.xml",
            "pagesXmlFilePath": "test/servers/psps/deploy/pages.xml"
        }
        self.assertTrue(pspsServer.load(config))

if __name__ == '__main__':
    unittest.main()

