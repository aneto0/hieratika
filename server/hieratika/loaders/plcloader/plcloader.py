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
__date__ = "22/02/2018"

##
# Standard imports
##
import bitstring
import configparser
import epics
import json
import logging
import time
import struct
from collections import OrderedDict
import numpy as np
from pvaccess import *

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
class PLCLoader(HieratikaLoader):
    """ A loader for the GCC Demo.
    """

    def __init__(self):
        super(HieratikaLoader, self).__init__()
        self.variableMap = {}
        self.variables = []
        self.pvLoadDigestName = ""
        self.pvLoadCounter = ""
        self.pvLoadCommand = ""
        self.pageName = "PLC_config"
        #self.fileId = open("config.fls", "w+b")
        self.fileId = open("config.json", "w")



    def load(self, config):
        """ Loads the mapping between the hieratika variables and the EPICS records, defined in a json file whose path shall be defined in
        [loader-impl] recordVariableMappingJsonPath
        """
        ok = False
        try:
            signalNames = config.get("loader-impl", "signalNames")
            self.variables.append(signalNames)
            signalModules = config.get("loader-impl", "signalModules")
            self.variables.append(signalModules)
            signalTriggerModes = config.get("loader-impl", "signalTriggerModes")
            self.variables.append(signalTriggerModes)
            functionNames = config.get("loader-impl", "functionNames")
            self.variables.append(functionNames)
            signalFunAssignment = config.get("loader-impl", "signalFunAssignment")
            self.variables.append(signalFunAssignment)
            signalFunLogic = config.get("loader-impl", "signalFunLogic")
            self.variables.append(signalFunLogic)
            signalFunOr = config.get("loader-impl", "signalFunOr")
            self.variables.append(signalFunOr)

            for pv in self.variables:
                print(pv)

            log.info("Going to be capable of loading the following variables: {0}".format(self.variables))

            ok = True
        except (ConfigParser.Error, KeyError, IOError) as e:
            log.critical(str(e))
            ok = False
        return ok

        return True

    def loadIntoPlant(self, pageName):
        log.info("Loading {0}".format(pageName))
        variablesPlantInfo = self.server.getVariablesInfo(self.pageName, self.variables)
        address = 0
        numberOfInputs=0
        signalInputValue=[[""]]
        signalNameValue=[""]
        functionNameValue=[""]
        functionSignalNameValue=[""]

        self.fileId.write("[");

        config_list = []

        #preprocessing input
        print("Preprocessing Stage")
        first = True
        for var in variablesPlantInfo:
            varName = var.getName()
            if varName=="DT@BT@DBLMA2":
                signalInputMode=var.getValue()
                for value in signalInputMode:
                    config=0
                    if value[0]=="Alarm signaled with 0":
                        config=1
                    elif value[0]=="Alarm signaled with 1":
                        config=2
                    elif value[0]=="Pulse Train":
                        config=0
                    else:
                        log.critical("Unrecognized signal mode {0}", signalInputMode)
                        return False
                    print(config, address)
                    if first:
                        first = False
                    else:
                        self.fileId.write(",");
                    #config_dict = OrderedDict([("Address_L", 2), ("Address_M", config%256), ("ID", config/256), ("Data_M", address%256), ("Data_L", address/256)])
                    #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                    #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : config%256, "Data_M" : config/256}
                    config_dict = OrderedDict([("ID", 2), ("Data_L", self.extractKBits(config,4,1)), ("Data_M", self.extractKBits(config,4,5)), ("Address_L", self.extractKBits(address,4,1)), ("Address_M", self.extractKBits(address,4,5))])
                    #self.fileId.write(struct.pack("4B",config%256, config/256, address%256, address/256))
                    self.fileId.write(json.dumps(config_dict));
                    config_list.append(config_dict)
                    address=address+1
                    #todo write it on file
            if varName=="DT@BT@DBLMA":
                signalInputValue=var.getValue()
                i=0
                for signalName in signalInputValue:
                    if i==0:
                        signalNameValue=[signalName[0]]
                    else:
                        signalNameValue=signalNameValue+[signalName[0]]
                    i=i+1
                signalInputValue=[['GND']]+signalInputValue;
                numberOfInputs=len(signalInputValue)
            if varName=="DT@BT@DBLSFS":
                functionNameValue=var.getValue()
                numberOfFunctions=len(functionNameValue)

        functionSignalNameValue=functionNameValue+signalNameValue
        #print(functionSignalNameValue)

        #signal assignment
        print("Function Assignment Stage")
        for var in variablesPlantInfo:
            varName = var.getName()
            #print(varName)
            if varName=="DT@BT@DBLMA3":
                funAssignmentValue=var.getValue()
                functionIndex=0

                for functionName in funAssignmentValue[0]:
                    inputIndex=0
                    for inputIn in funAssignmentValue:
                        signalIndex=0
                        config=0
                        for signalIn in signalInputValue:
                            signalName=signalIn[0]
                            #print(signalName, funAssignmentValue[inputIndex][functionIndex])
                            if signalName==funAssignmentValue[inputIndex][functionIndex]:
                                config=(1<<signalIndex)
                            signalIndex=signalIndex+1
                        print(config, address)
                        self.fileId.write(",");
                        #config_dict = OrderedDict([("Address_L", 2), ("Address_M", config%256), ("ID", config/256), ("Data_M", address%256), ("Data_L", address/256)])
                        #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                        config_dict = OrderedDict([("ID", 2), ("Data_L", self.extractKBits(config,4,1)), ("Data_M", self.extractKBits(config,4,5)), ("Address_L", self.extractKBits(address,4,1)), ("Address_M", self.extractKBits(address,4,5))])
                        #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : config%256, "Data_M" : config/256}
                        self.fileId.write(json.dumps(config_dict));
                        #self.fileId.write(struct.pack("4B",config%256,config/256,address%256,address/256))
                        config_list.append(config_dict)
                        address=address+1
                        inputIndex=inputIndex+1
                    functionIndex=functionIndex+1

        #function logic
        print("Function Logic Stage")
        for var in variablesPlantInfo:
            varName = var.getName()
            #print(varName)
            if varName=="DT@BT@DBLSFL":
                functionLogicValue=var.getValue()
                functionIndex=0
                maxVal=(2**(numberOfInputs))
                for functionName in functionLogicValue:
                   for signalTestVal in list(range(0, maxVal, 1)):
                       rowIndex=0
                       retVal=0
                       for functionInput in functionLogicValue[functionIndex]:
                           signalIndex=0
                           rowVal=1
                           for signalIn in signalInputValue:
                               inputIndex=0
                               for functionInput2 in functionLogicValue[functionIndex][rowIndex]:
                                   if signalIn[0]==funAssignmentValue[inputIndex][functionIndex]:
                                       if functionLogicValue[functionIndex][rowIndex][inputIndex]!= 'x':
                                           rowVal&=(int(functionLogicValue[functionIndex][rowIndex][inputIndex])==(signalTestVal>>(signalIndex)&1));
                                   inputIndex=inputIndex+1
                               signalIndex=signalIndex+1
                           rowIndex=rowIndex+1
                           retVal|=rowVal
                       #print(retVal,address,signalTestVal,functionIndex)
                       print(retVal,address)
                       self.fileId.write(",");
                       #config_dict = OrderedDict([("Address_L", 2), ("Address_M", retVal%256), ("ID", retVal/256), ("Data_M", address%256), ("Data_L", address/256)])
                       #config_dict = OrderedDict([("ID", 2), ("Data_L", retVal%256), ("Data_M", retVal/256), ("Address_L", address%256), ("Address_M", address/256)])
                       config_dict = OrderedDict([("ID", 2), ("Data_L", self.extractKBits(retVal,4,1)), ("Data_M", self.extractKBits(retVal,4,5)), ("Address_L", self.extractKBits(address,4,1)), ("Address_M", self.extractKBits(address,4,5))])
                       #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : retVal%256, "Data_M" : retVal/256}
                       self.fileId.write(json.dumps(config_dict));
                       #self.fileId.write(struct.pack("4B",retVal%256, retVal/256, address%256, address/256))
                       config_list.append(config_dict)
                       address=address+1
                   functionIndex=functionIndex+1

        #final OR
        print("Final ORs Stage")
        for var in variablesPlantInfo:
            varName = var.getName()
            #print(varName)
            if varName=="DT@BT@DBLSFO":
                finalOrValue=var.getValue()
                for orInput in finalOrValue:
                    for functionName in functionSignalNameValue:
                        config=0
                        elementIndex=0
                        for element in orInput[1]:
                            if element[0]==functionName:
                                logicIndex=0
                                for logic in orInput[2][elementIndex]:
                                    config|=(int(logic)<<logicIndex)
                                    logicIndex=logicIndex+1
                            elementIndex=elementIndex+1
                        print(config, address)
                        self.fileId.write(",");
                        config_dict = OrderedDict([("ID", 2), ("Data_L", self.extractKBits(config,4,1)), ("Data_M", self.extractKBits(config,4,5)), ("Address_L", self.extractKBits(address,4,1)), ("Address_M", self.extractKBits(address,4,5))])
                        #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                        self.fileId.write(json.dumps(config_dict));
                        #self.fileId.write(struct.pack("4B",config%256, config/256, address%256, address/256))
                        config_list.append(config_dict)
                        address=address+1
        self.fileId.write("]")
        self.fileId.flush()
        return True

    #Extract k bits from position p
    def extractKBits(self,num,k,p):
        binary = bin(num)
	#removing first two characters
        binary = binary[2:]
        end = len(binary) - p
        start = end -k + 1
        kBitSubStr = binary[start : end + 1]
        if kBitSubStr == '':
            splittedNum = 0
        else:
            splittedNum = int(kBitSubStr, 2)
        return splittedNum

    def isLoadable(self, pageName):
        return True
