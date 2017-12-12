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
__date__ = "22/11/2017"

##
# Standard imports
##
import logging

##
# Project imports
##
from variable import Variable

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class VariableLibrary(Variable):
    """ Describes a hieratika library variable. A variable library is a Variable whose value is the name of library contaning the parameter values that are to be assigned to a list of other variables. 
    """

    def __init__(self, name, alias, description = "", vtype = "", permissions = [], numberOfElements = [], value = [], libraryType = "", mappings = []):
        """ Constructs a new VariableLibrary object.
        
        Args:
            name (str): see Variable.__init__
            alias (str): see Variable.__init__
            description (str): see Variable.__init__
            vtype (str): see Variable.__init__
            numberOfElements ([int]): see Variable.__init__
            permissions (str): see Variable.__init__
            value (str): see Variable.__init__
            libraryType (str): the library type (which univocally defines the library in the system).
            mappings ([(source1:destination1), (source2, destination2), ...]): list of key/value tuples, where the key is the name of source variable in the library and the value is the name of destination parameter (where to copy the source variable value).
        """
        super(VariableLibrary, self).__init__(name, alias, description, vtype, permissions, numberOfElements, value, [])
        self.libraryType = libraryType
        self.mappings = mappings

    def getLibraryType(self):
        """ 
        Returns:
            The type of the library (which univocally defines the library in the system).
        """
        return self.libraryType

    def getMappings(self):
        """
        Returns:
            List of key/value tuples, where the key is the name of source variable in the library and the value is the name of destination parameter (where to copy the source variable value).
        """
        return self.mappings

    def asSerializableDict(self):
        """ 
        Returns:
            A json serializable representation of the Variable which serialises all of its properties and Variable members (see Variable.asSerializableDict) and the library description (name in a field name library and the mappings in a field named mappings (see getMappings())).
        """
        variable = super(VariableLibrary, self).asSerializableDict()
        variable["library"] = {}
        variable["library"]["type"] = self.getLibraryType()
        variable["library"]["mappings"] = self.getMappings()
        return variable

