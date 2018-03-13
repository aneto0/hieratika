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
__date__ = "22/12/2017"

##
# Standard imports
##
import ConfigParser
import epics
import json
import logging

##
# Project imports
##
from hieratika.monitor import HieratikaMonitor
from hieratika.variable import Variable

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class EPICSV3Monitor(HieratikaMonitor):
    """ Live variable monitoring of EPICS v3 variables.
    """

    def __init__(self):
        super(EPICSV3Monitor, self).__init__()
        self.variableCache = {}

    def pvValueChanged(self, pvname=None, value=None, **kw):
        """ Called everytime one of the monitored pvs changes"
            See http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
        """
        variables = {}
        variables[pvname] = value
        self.update(variables)

    def readCAInfoParameter(self, cainfoStr, parameter):
        """ Helper function which extract the parameter from the string returned by cainfo.
        
        Args:
            cainfoStr(str): value return by a cainfo of a given variable.
            parameter(str): parameter to be extracted.
        Returns:
            The parameter value or None if the parameter could not be found.
        """
        value = None
        parameter = "{0}=".format(parameter)
        splt = cainfoStr.split(parameter)
        if (len(splt) > 1):
            value = splt[1].split("\n")[0]
        else:
            log.critical("Failed to get parameter {0} from cainfo {1}".format(parameter, cainfoStr))

        return value

    def convertVariableTypeFromCAInfo(self, vtype):
        """ Helper function which converts the vtype returned by cainfo into an hieratika type.
        
        Args:
            parameter(str): vtype type to be converted.
        Returns:
            The converted type (which will be string if not found).
        """
        ret = "string"
        if (vtype == "string"):
            ret = "string"
        elif (vtype == "int"):
            ret = "int32"
        elif (vtype == "short"):
            ret = "int16"
        elif (vtype == "float"):
            ret = "float32"
        elif (vtype == "enum"):
            ret = "enum"
        elif (vtype == "char"):
            ret = "int8"
        elif (vtype == "long"):
            ret = "int32"
        elif (vtype == "double"):
            ret = "float64"
        elif (vtype == "time_string"):
            ret = "string"
        elif (vtype == "time_int"):
            ret = "int32"
        elif (vtype == "time_short"):
            ret = "int16"
        elif (vtype == "time_float"):
            ret = "float32"
        elif (vtype == "time_enum"):
            ret = "enum"
        elif (vtype == "time_char"):
            ret = "int8"
        elif (vtype == "time_long"):
            ret = "int32"
        elif (vtype == "time_double"):
            ret = "float64"
        elif (vtype == "ctrl_string"):
            ret = "string"
        elif (vtype == "ctrl_int"):
            ret = "int8"
        elif (vtype == "ctrl_short"):
            ret = "int16"
        elif (vtype == "ctrl_float"):
            ret = "float32"
        elif (vtype == "ctrl_enum"):
            ret = "enum"
        elif (vtype == "ctrl_char"):
            ret = "int8"
        elif (vtype == "ctrl_long"):
            ret = "int32"
        elif (vtype == "ctrl_double"):
            ret = "float64"
        return ret

    def loadVariable(self, pvName):
        """ Populates a Variable by cainfoing the pvName

        Args:
            pvName(str): the name of the pv.
        Returns:
            A variable describing the pv or None if the cainfo fails.
        """
        cainfoStr = epics.cainfo(pvName, False)
        variable = None
        if (cainfoStr is not None):
            #Remove white spaces
            cainfoStr = "".join(cainfoStr.split(" "))
            vtype = self.readCAInfoParameter(cainfoStr, "type")
            nelm = int(self.readCAInfoParameter(cainfoStr, "nelm"))
            value = epics.caget(pvName)
            if (nelm > 1):
                value = value.tolist()
            if ((value is not None) and (vtype is not None) and (nelm is not None)):
                variable = Variable(pvName, pvName, "", vtype, [], [nelm], [value])
                log.debug("Loading {0}".format(variable))
        else:
            log.critical("Failed to cainfo pv {0}".format(pvName))
        return variable

    def getLiveVariablesInfo(self, requestedVariables):
        variables = []
        for varname in requestedVariables:
            log.debug("Looking for variable {0}".format(varname))
            if varname in self.variableCache:
                variable = self.variableCache[varname]
                log.debug("Going to caget {0}".format(varname))
                value = epics.caget(varname)
                log.debug("caget {0} = {1}".format(varname, value))
                if (value is not None):
                    nelm = variable.getNumberOfElements()
                    if (nelm > 1):
                        try:
                            value = value.tolist()
                        except Exception as e:
                            log.critical("Could not convert value to list {0}".format(e))
                    variable.setValue(value)
                variables.append(variable)

        return variables

    def load(self, config):
        """  Registers with a camonitor the variable names defined in a json file whose path shall be defined in
        [monitor-impl] variableListJsonPath
        """
        ok = False
        try:
            jsonFileName = config.get("monitor-impl", "variableListJsonPath")
            with open(jsonFileName) as jsonFile:
                variableList = json.load(jsonFile)
                for pvName in variableList:
                    var = self.loadVariable(pvName)
                    if (var is not None):
                        log.info("Going to monitor {0}".format(pvName))
                        self.variableCache[pvName] = var
                        epics.camonitor(pvName, None, self.pvValueChanged)
            ok = True
        except (ConfigParser.Error, KeyError, IOError) as e:
            log.critical(str(e))
            ok = False
        return ok

    def loadCommon(self, config):
        return True


