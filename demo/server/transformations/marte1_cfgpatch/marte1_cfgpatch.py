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
__date__ = "30/01/2018"

##
# Standard imports
##
import cdb
import logging

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
class MARTe1CfgPatch(HieratikaTransformation):
    """ Patches a MARTe1 configuration file.
        Needs the CCFE cdb py implementation (see https://git.ccfe.ac.uk/edwardsj/martepy/)
    """
    
    def __init__(self):
        super(MARTe1CfgPatch, self).__init__()
        
    def load(self, config):
        return True

    def loadCommon(self, config):
        return True

    def transform(self, transformationUID, fun, inputs):
        """ Patches all the input variables in the configuration inputCfg. Writes output to OutputCfg.
            Each input variable is assumed to be a cdb structured separated with a .
        """
        outputs = {}
        try:
            inputCfg = inputs["InputCfg"]
            config = cdb.read_cdb_string(inputCfg)

            for variable in inputs:
                if variable == "InputCfg":
                    continue
                #Structure separator is .:
                keys = variable.split(".")
                #Navigate in the MARTe configuration file (e.g. MARTe.Thread_1.GAMs.Param1)
                p = config
                for k in keys[:-1]:
                    p = p[k]
                p[keys[-1]] = "\"{0}\"".format(inputs[variable])

            outputs["OutputCfg"] = "\"{0}\"".format(config.serialise())
        except Exception as e:
            log.critical("Could not transform configuration file {0}".format(e))
        self.update(transformationUID, 0, 1, outputs)
        return True

    def isTransformationSupported(self, fun, inputs):
        """ Must have at least the InputCfg and the OutputCfg parameters defined.
        """
        ok = (fun == "marte1_cfgpatch")
        if (ok):
            ok = "InputCfg" in inputs

        log.debug("isTransformationSupported {0} ? {1}".format(fun, ok))
        return ok

