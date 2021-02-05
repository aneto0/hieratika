#!/usr/bin/env python

from __future__ import absolute_import
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
__date__ = "18/12/2017"

##
# Standard imports
##
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
class TransformationFunction(object):
    """ Describes a hieratika transformation function.
    """

    def __init__(self, fun, description, inputs, outputs):
        """ Constructs a new TransformationFunction object.
        
        Args:
            fun (str): the function name. 
            description (str): the function description. 
            inputs ({var1:id1, var2:id2, ...}): a dictionary whose keys are the name of the function input variables and whose values are the id of the variables (see Variable) where the function parameter values should be read from. 
            outputs ({var1:id1, var2:id2, ...}): a dictionary whose keys are the name of the function ouput variables and whose values are the id of the variables (see Variable) where the function parameter value should written into. 
        """
        self.fun = fun
        self.description = description
        self.inputs = inputs
        self.outputs = outputs

    def getFunction(self):
        """ 
        Returns: 
            The function name (see __init__).
        """
        return self.fun

    def setFunction(self, fun):
        """ Sets the function name.
        
        Args:
            fun(str): the new function name.
        """
        self.fun = fun

    def getInputs(self):
        """ 
        Returns: 
            The function input variables names (see __init__).
        """
        return self.inputs

    def getOutputs(self):
        """
        Returns:
            The function output variables names (see __init__)
        """
        return self.outputs

    def getDescription(self):
        """
        Returns:
            The function description. 
        """
        return self.description

    def getUID(self):
        """
        Returns:
        	A unique identifier for the TransformationFunction based on the function name, input variables names and output variables names.
        """
        return "{0}_{1}_{2}".format(self.fun, list(self.inputs.keys()), list(self.outputs.keys()))

    def __eq__(self, another):
        """ Two TransformationFunction are equal if they have the same unique identifier (see getUID).
           
        Args:
            self (Variable): this TransformationFunction instance.
            another (Variable or str): another TransformationFunction or a string. 
        Returns:
            True if self and another TransformationFunction are equal or if another is a string whose value is the self.getUID().
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getUID() == another.getUID())
        else:
            areEqual = (self.getUID() == str(another))
        return areEqual

    def __cmp__(self, another):
        """ See __eq__
        """
        return (self == another) 

    def __hash__(self):
        """ The class is univocally identified by the UID (see getUID).

        Returns:
            The UID of the TransformationFunction.
        """
        return getUID()

    def __str__(self):
        """ Returns a string representation of a Variable.
            
            Returns:
                A string representation of a Variable which consists of the function name followed by the input and output variables.
        """
        return "{0} = {1}({2})".format(list(self.outputs.keys()), self.fun, list(self.inputs.keys())) 

