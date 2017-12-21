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
__date__ = "21/12/2017"

##
# Standard imports
##
import logging
import os
import pvaccess 
import SupConfigurationRPCClient

##
# Project imports
##
from hieratika.loader import HieratikaLoader

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class SUPLoader(HieratikaLoader):
    """ ITER SUP implementation.
    """
    
    def __init__(self):
        super(HieratikaLoader, self).__init__()
        
    def load(self, manager, config):
        ok = True
        try:
            self.baseDir = config.get("loader-impl", "baseDir")
        except (ConfigParser.Error, KeyError) as e:
            log.critical(str(e))
            ok = False 
    
        return ok

    def loadIntoPlant(self, pageName):
        log.info("Loading {0}".format(pageName)) 
        ok = True
        try:
            SupConfigurationRPCClient.apply(xmlPath)
        except pvaccess.PvaException as e:
            log.error("RPC Exception: %s" % e.message)
            ok = False
        return ok

    def isLoadable(self, pageName):
        xmlPath = "{0}/psps/configuration/{1}/000/plant.xml".format(self.baseDir, pageName)
        return os.path.exists(xmlPath)


