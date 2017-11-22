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
from scriptorium.variable import Variable

##
# Logger configuration
##
logging.basicConfig(level=logging.DEBUG)

##
# Class definition
##
class TestVariable(unittest.TestCase):

    def test_init(self):
        var1 = Variable("AA", "AA", "", "")
        var1.addMember(Variable("BB", "BB", "", ""))
        var1BB = var1.getMember("BB")
        var1BB.addMember(Variable("CC", "CC", "int32", "", [], [1]))
        var1BB.addMember(Variable("DD", "DD", "float32", "", [], [1,2]))
        var1CC = var1BB.getMember("CC")
        var1CC = var1BB.getMember("DD")
        print (json.dumps(var1.asSerializableDict(), indent=4, sort_keys=True))
        #print var1BB.__dict__
        #print var1CC.__dict__
        #print var1DD.__dict__

if __name__ == '__main__':
    unittest.main()

