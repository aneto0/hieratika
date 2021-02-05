#!/usr/bin/env python
from __future__ import absolute_import
import six
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
from abc import ABCMeta, abstractmethod
import json
import logging

##
# Project imports
##

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class HieratikaTransformation(six.with_metaclass(ABCMeta, object)):
    """ Abstract class for any transformation implementation.
        TODO
    """

    def __init__(self):
        pass
        
    @abstractmethod
    def load(self, manager, config):
        """ Configures the transformation against a set of parameters. This set of parameters is specific for each transformation implementation.
        
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
            config(ConfigParser): the transformation specific implementation parameters are in the section "transformation-impl".
        Returns:
            True if the transformation is successfully configured.
        """
        pass

    @abstractmethod
    def transform(self, transformationUID, fun, inputs):
        """ Executes the transformation function against the provided inputs.
            Note that the outputs are to be streamed through a different interface (see update).
            
        Args:
            transformationUID (str): unique identifier for the transformation (one for each call to this function) to be used when calling the update method.
            fun (str): name of the function to be executed.
            inputs ({variableName1:value1, variableName2:value2, ...}):  dictionary with variables to be used as input to the function.
        Returns:
            None
        """
        pass

    @abstractmethod
    def isTransformationSupported(self, fun, inputs):
        """ Returns True if the transformation defined by fun and by list of inputs can be executed by this HieratikaTransformation instance.
        
        Args:
            fun (str): name of the function to be executed.
            inputs ({variableName1:value1, variableName2:value2, ...}):  dictionary with variables to be used as input to the function.
        Returns:
            None
        """
        pass

    def loadCommon(self, manager, config):
        """ Loads parameters that are common to all transformation implementations.
            NOOP as of today.
            
        Args:
            manager(multiprocessing.Manager): A multiprocessing Manager instance to allocate objects that are to be shared by different processes.
        Returns:
            True 
        """
        return True

    def setServer(self, server):
        """ Sets the server implementation.
        
        Args:
            server (Server): the server implementation.
        """
        self.server = server

    def update(self, transformationUID, state, progress, outputs):
        """ Informs about the state of the transformation identified by the transformationUID. 
        
        Args:
            transformationUID (str): unique identifier of the transformation.
            state (int): execution state as one of the following: 0: RUNNING; 1: COMPLETED; -1: ERROR.
            progress (float): number between 0 and 1 with the current execution progress (when RUNNING).
            outputs ({variableName1:value1, variableName2:value2, ...}):  dictionary with the variables that have been updated.
        Returns:
            None
        """
        toStream = {
            "transformationUID": transformationUID,
            "state": state,
            "progress": progress,
            "outputs": outputs
        }
        self.server.queueStreamData(json.dumps(toStream))


