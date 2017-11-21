import logging
import time
import unittest

from scriptorium.servers.psps.pspsserver import PSPSServer

logging.basicConfig(level=logging.DEBUG)

class TestPSPSServer(unittest.TestCase):

    def setUp(self):
        pass

    def test_constructor(self):
        pspsServer = PSPSServer()
        self.assertTrue(True)

    def test_load(self):
        pspsServer = PSPSServer()
        config = {
            "baseDir": "/tmp",
            "numberOfLocks": 8,
            "usersXmlFilePath": "test/servers/psps/users.xml",
            "pagesXmlFilePath": "test/servers/psps/pages.xml"
        }
        self.assertTrue(pspsServer.load(config))

if __name__ == '__main__':
    unittest.main()

