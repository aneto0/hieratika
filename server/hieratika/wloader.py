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
from flask import Response
import json
import logging
import time
import threading

##
# Project imports
##
from hieratika.hconstants import HieratikaConstants

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class WLoader(object):
    """ Provides an interface point between the specific loader implementations (see HieratikaLoader)
        and the webserver. In particular this class parses and transforms the web form parameters into 
        the list of the parameters that are expected by the HieratikaLoader implementation.
    """

    def __init__(self):
        """ NOOP
        """
        self.loaderImpls = []

    def setLoaders(self, loaderImpls):
        """ Sets the HieratikaLoader implementations to be used.
        
        Args:
            loaderImpls ([HieratikaLoader]): the list of HieratikaLoader implementations to be used.
        """
        self.loaderImpls = loaderImpls

    def loadIntoPlant(self, request):
        """ Parses the web parameters and loads (in order) the specified plants.

        Args:
            request.form["pageNames"]: the name of the configuration models that are to be loaded.
        Returns:
            HieratikaConstants.OK if all the configurations are successfully loaded.
        """
        toReturn = "InvalidParameters"
        try:
            pageNames = json.loads(request.form["pageNames"])
            ok = True
            for pageName in pageNames:
                found = False
                for loader in self.loaderImpls:
                    found = loader.isLoadable(pageName)
                    if (found):
                        log.info("Loading into the plant the page with name {0}".format(pageName))
                        ok = loader.loadIntoPlant(pageName)
                        if (ok):
                            log.info("Loaded into the plant the page with name {0}".format(pageName))
                        else:
                            log.critical("Failed loading into the plant the page with name {0}".format(pageName))
                            break
                        #Do not break if found
                if (not found):
                    log.critical("Could not found a loader for the page with name {0}".format(pageName))
                if (not ok):
                    break
            if (ok):
                toReturn = HieratikaConstants.OK            
        except KeyError as e:
            log.critical(e)
        return toReturn

