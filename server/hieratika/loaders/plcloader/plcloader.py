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
import ConfigParser
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
# HelperTools
##

def InitTable(table, poly, table_init):
    status = (table_init == False)
    if status == True:
        for table_index in range(256):
            tempCRC = table_index
            for bit_index in range(8):
                if 0x01 == (seed & 0x01):
                    tempCRC = poly ^ (seed >> 1)
                else:
                    tempCRC = tempCRC >> 1
            table[table_index] = tempCRC
        table_init = True
        status = True
    return status
    
def ComputeChecksum(cfg_list, seed, checksum):
    checksum = 0xFFFFFFFF
    seed_bytes = struct.pack('<I', seed)
    s1 = np.asarray(struct.unpack('<B',seed_bytes[0]))
    s2 = np.asarray(struct.unpack('<B',seed_bytes[1]))
    s3 = np.asarray(struct.unpack('<B',seed_bytes[2]))
    s4 = np.asarray(struct.unpack('<B',seed_bytes[3]))
    
    if seed != 0:
        checksum = table[(checksum ^ s1[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s2[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s3[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s4[0]) & 0xFF] ^ (checksum >> 8)
    
    for index in range(3213):
        checksum = table[(checksum ^ cfg_list[index]['Address_L']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Address_M']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['ID']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Data_M']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Data_L']) & 0xFF] ^ (checksum >> 8)
        
    checksum = checksum ^ 0xFFFFFFFF
    
    checksum = checksum % (1<<32) #convert to unsigned 32
    print "cacca ",checksum
    
    return crc

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
        #self.fileId = open("config.json", "w")
        
    

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

        #self.fileId.write("[");
        
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
                    #else:
                    #    self.fileId.write(",");
                    config_dict = OrderedDict([("Address_L", 2), ("Address_M", config%256), ("ID", config/256), ("Data_M", address%256), ("Data_L", address/256)])
                    #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                    #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : config%256, "Data_M" : config/256}
                    #self.fileId.write(struct.pack("4B",config%256, config/256, address%256, address/256))
                    #self.fileId.write(json.dumps(config_dict));
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
                        #self.fileId.write(",");
                        config_dict = OrderedDict([("Address_L", 2), ("Address_M", config%256), ("ID", config/256), ("Data_M", address%256), ("Data_L", address/256)])
                        #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                        #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : config%256, "Data_M" : config/256}
                        #self.fileId.write(json.dumps(config_dict));
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
                       #self.fileId.write(",");
                       config_dict = OrderedDict([("Address_L", 2), ("Address_M", retVal%256), ("ID", retVal/256), ("Data_M", address%256), ("Data_L", address/256)])
                       #config_dict = OrderedDict([("ID", 2), ("Data_L", retVal%256), ("Data_M", retVal/256), ("Address_L", address%256), ("Address_M", address/256)])
                       #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : retVal%256, "Data_M" : retVal/256}
                       #self.fileId.write(json.dumps(config_dict));
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
                        #self.fileId.write(",");
                        config_dict = OrderedDict([("Address_L", 2), ("Address_M", config%256), ("ID", config/256), ("Data_M", address%256), ("Data_L", address/256)])
                        #config_dict = OrderedDict([("ID", 2), ("Data_L", config%256), ("Data_M", config/256), ("Address_L", address%256), ("Address_M", address/256)])
                        #config_dict = {"ID" : 2, "Address_L" : address%256, "Address_M" : address/256, "Data_L" : config%256, "Data_M" : config/256}
                        #self.fileId.write(json.dumps(config_dict));
                        #self.fileId.write(struct.pack("4B",config%256, config/256, address%256, address/256))
                        config_list.append(config_dict)
                        address=address+1
        #self.fileId.write("]")
        #self.fileId.flush()
        #Setting up RPCClient
        rpc = RpcClient('55a0::Cfg::Interface')
        rpc.setTimeout(30.0)

        #Reading configuration
        readRequest = PvObject({'qualifier' : STRING})
        readRequest.setString('qualifier', 'read')
        print "INFO PLCLoader -- Reading configuration..."
        readResponse = rpc.invoke(readRequest)
        status = readResponse.getBoolean('status')
        if status != True:
            print "...failure"
        else:
            print "...success"

        #Initialisation
        #Retrieving first the seed
        status = None
        initRequest = PvObject({'qualifier' : STRING})
        initRequest.setString('qualifier', 'init')
        print "INFO PLCLoader -- Retrieving seed..."
        initResponse = rpc.invoke(initRequest)
        status = initResponse.getBoolean('status')
        if status != True:
            print "...failure"
        else:
            print "...success"

        seed = initResponse.getUInt('value')
        print "...",seed,"..."

        #Initialise table for checksum
        table = [None] * 256
        poly = 0xEDB88320
        table_init = False
        #InitTable(table, poly, table_init)

        #Loading configuration
        loadRequest = PvObject({'qualifier' : STRING, 'seed' : UINT, 'hash' : UINT, 'value' : [{'ID' : UBYTE, 'Data_L' : UBYTE, 'Data_M' : UBYTE, 'Address_L' : UBYTE, 'Address_M' : UBYTE}]})
        loadRequest.setString('qualifier', 'load')
        cfg_list = readResponse.getStructureArray('value')

        for i in range(0,3213): 
            cfg_list[i]['Address_L'] = config_list[i]['Address_L'] #ID
            cfg_list[i]['Address_M'] = config_list[i]['Address_M'] #Data_L
            cfg_list[i]['ID'] = config_list[i]['ID'] #Data_M
            cfg_list[i]['Data_M'] = config_list[i]['Data_M'] #Address_L
            cfg_list[i]['Data_L'] = config_list[i]['Data_L'] #Address_M
            
        loadRequest.setStructureArray(cfg_list)

        #Compute checksum
        crc = None
        print "INFO PLCLoader -- Computing checksum..."
        #crc = ComputeChecksum(cfg_list, seed, crc)
        print "...",crc,"..."
            
        loadRequest.setUInt('seed', seed)
        loadRequest.setUInt('hash', 0)
        print type(loadRequest['value'])
        print "INFO PLCLoader -- Loading configuration..."
        loadResponse = rpc.invoke(loadRequest)
        status = loadResponse.getBoolean('status')
        if status != True:
            print "...failure"
        else:
            print "...success"    
        return True

    def isLoadable(self, pageName):
        return True

