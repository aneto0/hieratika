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
__date__ = "18/12/2017"

##
# Standard imports
##
from ahkab import new_ac, run
from ahkab.circuit import Circuit
from abc import ABCMeta, abstractmethod
import json
import logging
import numpy as np
import time

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
class AhkabDemo(HieratikaTransformation):
    """ Demo transformation class which implements the filter defined in http://ahkab.readthedocs.io/en/latest/examples/Python_API.html.
        TODO
    """
    
    __metaclass__ = ABCMeta

    def __init__(self):
        super(HieratikaTransformation, self).__init__()
        
    def load(self, manager, config):
        return True

    def loadCommon(self, manager, config):
        return True

    def transform(self, transformationUID, fun, inputs):
        cir = Circuit("Butterworth band-pass filter")
        cir.add_vsource("V1", "n1", cir.gnd, dc_value=0., ac_value=inputs["V1"])
        cir.add_resistor("R1", "n1", "n2", inputs["R1"])
        cir.add_inductor("L1", "n2", "n3", inputs["L1"])
        cir.add_capacitor("C1", "n3", "n4", inputs["C1"])
        cir.add_inductor("L2", "n4", cir.gnd, inputs["L2"])
        cir.add_capacitor("C2", "n4", cir.gnd, inputs["C2"])
        cir.add_inductor("L3", "n4", "n5", inputs["L3"])
        cir.add_capacitor("C3", "n5", "n6", inputs["C3"])
        cir.add_inductor("L4", "n6", cir.gnd, inputs["L4"])
        cir.add_capacitor("C4", "n6", cir.gnd, inputs["C4"])
        cir.add_capacitor("C5", "n7", "n8", inputs["C5"])
        cir.add_inductor("L5", "n6", "n7", inputs["L5"])
        cir.add_resistor("R2", "n8", cir.gnd, inputs["R2"])

        numberOfSteps = 10
        startFrequency = inputs["FS"]
        endFrequency = inputs["FE"]
        deltaFrequency = (endFrequency - startFrequency)
        numberOfPoints = inputs["PTS"]
        stepFrequency = (deltaFrequency / numberOfSteps)
        stepPoints = numberOfPoints / numberOfSteps
        if ((stepFrequency == 0) or (stepPoints == 0)):
            stepPoints = numberOfPoints
            stepFrequency = (endFrequency - startFrequency) + 1
        freq = startFrequency
        while(freq <= endFrequency):
            log.debug("Simulating circuit between {0} and {1} Hz".format(freq, freq + stepFrequency))
            ac1 = new_ac(freq, freq + stepFrequency, stepPoints, x0=None)
            # run it
            res = run(cir, ac1)
            outputs = {}
            fout = res["ac"]["f"].tolist()
            outputs["VOUT"] = [fout, np.abs(res["ac"]["Vn8"]).tolist()]
            outputs["VANGLE"] = [fout, np.angle(res["ac"]["Vn8"]).tolist()]
            progress = float(freq - startFrequency) / float(deltaFrequency)
            freq = freq + stepFrequency
            self.update(transformationUID, 0, progress, outputs)
            time.sleep(1)

        return True

    def isTransformationSupported(self, fun, inputs):
        ok = (fun == "ahkab_butterworth")
        if (ok):
            ok = "R1" in inputs
        if (ok):
            ok = "L1" in inputs
        if (ok):
            ok = "C1" in inputs
        if (ok):
            ok = "L2" in inputs
        if (ok):
            ok = "C2" in inputs
        if (ok):
            ok = "L3" in inputs
        if (ok):
            ok = "C3" in inputs
        if (ok):
            ok = "L4" in inputs
        if (ok):
            ok = "C4" in inputs
        if (ok):
            ok = "L5" in inputs
        if (ok):
            ok = "C5" in inputs
        if (ok):
            ok = "R2" in inputs
        if (ok):
            ok = "V1" in inputs
        if (ok):
            ok = "FS" in inputs
        if (ok):
            ok = "FE" in inputs
        if (ok):
            ok = "PTS" in inputs

        log.debug("isTransformationSupported {0} ? {1}".format(fun, ok))
        return ok

