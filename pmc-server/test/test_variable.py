import json
import logging
import time
import unittest

from scriptorium.variable import Variable

logging.basicConfig(level=logging.DEBUG)

class TestVariable(unittest.TestCase):

    def test_init(self):
        var1 = Variable("AA", "AA", "", "", "")
        member1 = Variable("BB", "BB", "", "", "", var1)
        var1["BB"] = member1
        print member1.getAbsoluteName()
        print member1.getName()
        print var1["BB"].__dict__

if __name__ == '__main__':
    unittest.main()

