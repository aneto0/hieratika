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
__date__ = "17/12/2017"

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
from hieratika.transformation import HieratikaTransformation 

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class WTransformation:
    """ Provides an interface point between the specific transformaton implementations (see HieratikaTransformation)
        and the webserver. In particular this class parses and transforms the web form parameters into 
        the list of the parameters that are expected by the HieratikaTransformation implementation.
    """

    def __init__(self):
        """ NOOP
        """
        self.transformationCache = {}

    def getTransformationUID(self, fun, inputs):
        """ 
        Args: 
            fun (str): name of the function to be executed.
            inputs ([variableName1, variableName2, ...]): list with the name of the transformation input variables.
        Returns:
            A unique id for a transformation based on the the function name and on the inputs.
        """
        return "{0}.{1}".format(fun, len(inputs))

    def setTransformations(self, transformationImpls):
        """ Sets the HieratikaTransformation implementations to be used.
        Args:
            transformationImpls ([HieratikaTransformation]): the list of HieratikaTransformation implementations to be used.
        """
        self.transformationImpls = transformationImpls

    def transformCb(self, transformationImpl, transformationUID, fun, inputs):
        """ TODO
        """
        transformationImpl.transform(transformationUID, fun, inputs)

    def transform(self, request):
        """ Parses the web parameters and executes the transformation function against the provided inputs.

        Args:
            request.form["fun"]: the name of the function to execute.
            request.form["inputs"]: a dictionary with the list of the variables to be used as input to the function in the form {variableName1:variableValue1, ...}
        Returns:
            The unique identifier of the transformation function or InvalidParameters if the transformation function could not be created.
        """
        toReturn = "InvalidParameters"
        try:
            fun = request.form["fun"]
            inputs = json.loads(request.form["inputs"])

            transformationImpl = None
            funUID = self.getTransformationUID(fun, inputs)
            log.debug("Looking for existent transformation cache with UID {0}".format(funUID))
            if funUID in self.transformationCache:
                transformationImpl = self.transformationCache[funUID]
                log.debug("Found existent transformation cache with UID {0}".format(funUID))
            else:
                for tr in self.transformationImpls:
                    if (tr.isTransformationSupported(fun, inputs)):
                        transformationImpl = tr
                        break

            if (transformationImpl is not None):
                log.critical("Executing transformation for function with UID {0}".format(funUID))
                transformationUID = str(time.time())
                transformationThread = threading.Thread(target=self.transformCb, args=(transformationImpl, transformationUID, fun, inputs, ))
                transformationThread.daemon = True
                transformationThread.start()
                toReturn = transformationUID
            else:
                log.critical("Could not find transformation for function with UID {0}".format(funUID))
        except KeyError as e:
            log.critical(e)
        return toReturn

