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
        return True

if __name__ == '__main__':
    unittest.main()

