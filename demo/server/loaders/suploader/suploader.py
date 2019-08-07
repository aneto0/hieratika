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
__date__ = "05/08/2019"

##
# Standard imports
##
import ConfigParser
import binascii
import crcmod
import json
import pvaccess
import logging
import struct
import time

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
class SUPLoader(HieratikaLoader):
    """ A loader for the ITER SUP.
    """
    
    def __init__(self):
        super(HieratikaLoader, self).__init__()
        self.variableMap = {}
        self.variables = []
        self.pageName = "55A0-sup-demo"

    def load(self, config):
        """ TODO TODO Loads the mapping between the hieratika variables and the EPICS records, defined in a json file whose path shall be defined in
        [loader-impl] recordVariableMappingJsonPath 
        """
        ok = False
        try:
           jsonFileName = config.get("loader-impl", "variableListJsonPath")
           with open(jsonFileName) as jsonFile:
               self.variableMap = json.load(jsonFile)
           for pv in self.variableMap:
               self.variables.append(pv)

           log.info("Going to be capable of loading the following variables: {0}".format(self.variableMap))

           ok = True
        except (ConfigParser.Error, KeyError, IOError) as e:
           log.critical(str(e))
           ok = False
        return ok

    def getPVObjectDict(self, var):
        ret = {}
        members = var.getMembers()
        for m in members:
            member = members[m]
            if (member.IsStruct()):
                ret[m] = self.getPVObjectDict(member)
            else:
                nelems = member.getNumberOfElements()
                totElements = 0
                try:
                    for n in nelems:
                        totElements += n
                except:
                    totElements = 1
                isArray = (totElements > 1)
                if (member.getType() == "uint32"):
                    if (isArray):
                        ret[m] = [pvaccess.ScalarType.UINT]
                    else:
                        ret[m] = pvaccess.ScalarType.UINT
                elif (member.getType() == "int32"):
                    if (isArray):
                        ret[m] = [pvaccess.ScalarType.INT]
                    else:
                        ret[m] = pvaccess.ScalarType.INT
                elif (member.getType() == "uint64"):
                    if (isArray):
                        ret[m] = [pvaccess.ScalarType.ULONG]
                    else:
                        ret[m] = pvaccess.ScalarType.ULONG
                elif (member.getType() == "int64"):
                    if (isArray):
                        ret[m] = [pvaccess.ScalarType.LONG]
                    else:
                        ret[m] = pvaccess.ScalarType.LONG
                elif (member.getType() == "float32"):
                    if (isArray):
                        ret[m] = [pvaccess.ScalarType.FLOAT]
                    else:
                        ret[m] = pvaccess.ScalarType.FLOAT

        return ret

    def getPVObjectValue(self, var):
        members = var.getMembers()
        ret = {}

        for m in members:
            member = members[m]
            nelems = member.getNumberOfElements()
            totElements = 0
            try:
                for n in nelems:
                    totElements += n
            except:
                totElements = 1
            isArray = (totElements > 1)

            if (member.IsStruct()):
                ret[m] = self.getPVObjectValue(member)
            else:
                val = member.getValue()
                if (isArray):
                    ret[m] = val
                else:
                    try:
                        val = val[0]
                    except:
                        val = val
            ret[m] = val
        return ret

    def computeCRC(self, data):
        log.debug("Computing CRC for {0} bytes".format(len(data)))
        crc32Func = crcmod.mkCrcFun(0x104c11db7, initCrc=0xFFFFFFFF, rev=False, xorOut=0x0)
        return crc32Func(data) 

    def getBinaryValue(self, val, hType):
        t = "h"
        if (hType == "uint8"):
            t = "B"
        elif (hType == "int8"):
            t = "b"
        elif (hType == "uint16"):
            t = "H"
        elif (hType == "int16"):
            t = "h"
        elif (hType == "uint32"):
            t = "I"
        elif (hType == "int32"):
            t = "i"
        elif (hType == "uint64"):
            t = "Q"
        elif (hType == "int64"):
            t = "q"
        elif (hType == "float32"):
            t = "f"
        elif (hType == "float64"):
            t = "d"
        else:
            log.critical("Unrecognised type {0}".format(hType))
        #log.debug("getBinaryValue for type {0} is {1}".format(hType, t))
        ret = struct.pack(t, val)
        return ret

    def getBinary(self, var, ret = ""):
        members = var.getMembers()
        for m in members:
            member = members[m]
            if (member.IsStruct()):
                ret += self.getBinary(member)
            else:
                val = member.getValue()
                #For the time being only 1D arrays
                if (type(val) == list):
                    for v in val:
                        ret += self.getBinaryValue(v, member.getType())
                else:
                    ret += self.getBinaryValue(val, member.getType())
        return ret

    def getBinaryValueFromPVA(val, pvaType):
        """ As getBinaryValue but from a PVA (which does not guarantee order
        """
        try:
            #We might receive a type inside an array
            if (len(pvaType) > 0):
                pvaType = pvaType[0]
        except:
            t = "h"

        t = "h"
        if (pvaType == pvaccess.ScalarType.BOOLEAN):
            t = "?"
        elif (pvaType == pvaccess.ScalarType.UBYTE):
            t = "B"
        elif (pvaType == pvaccess.ScalarType.BYTE):
            t = "b"
        elif (pvaType == pvaccess.ScalarType.USHORT):
            t = "H"
        elif (pvaType == pvaccess.ScalarType.SHORT):
            t = "h"
        elif (pvaType == pvaccess.ScalarType.UINT):
            t = "I"
        elif (pvaType == pvaccess.ScalarType.INT):
            t = "i"
        elif (pvaType == pvaccess.ScalarType.ULONG):
            t = "Q"
        elif (pvaType == pvaccess.ScalarType.LONG):
            t = "q"
        elif (pvaType == pvaccess.ScalarType.FLOAT):
            t = "f"
        elif (pvaType == pvaccess.ScalarType.DOUBLE):
            t = "d"
        else:
            log.critical("Unrecognised type {0}".format(hType))
        ret = struct.pack(t, val)
        return ret

    def getBinaryFromPVA(responseValue, responseValueStruct):
        """ As getBinary but from a PVA (which does not guarantee order)
        """
        ret = ""
        for k,v in responseValue.items():        
            if isinstance(v, dict):
                ret += GetBinaryImage(v, responseValueStruct[k])
            if isinstance(v, list):
                for l in v:
                    ret += GetBinaryValue(l, responseValueStruct[k])
            else: 
                ret += GetBinaryValue(v, responseValueStruct[k])
        return ret


    def checkPlantStructure(self, var, pvObjValueStructureDict):
        #Get the current supported structure from the plant and compare with the one from pvObj
        fullVarName = var.getAbsoluteName()
        rpcClientAddress = str(self.variableMap[var.getAbsoluteName()]["rpc"])
        rpc = pvaccess.RpcClient(rpcClientAddress)
        request = pvaccess.PvObject({"qualifier": pvaccess.STRING})
        request.set({"qualifier": "read"})
        response = rpc.invoke(request)
        expectedStructure = response.getStructureDict()["value"]
        ok = (expectedStructure == pvObjValueStructureDict)
        if (not ok):
            log.critical("For variable {0}, expected {0} and want to load {1}".format(var.getAbsoluteName(), expectedStructure, pvObj.getStructureDict())) 
        return ok

    def getPlantSeed(self, var):
        fullVarName = var.getAbsoluteName()
        rpcClientAddress = str(self.variableMap[var.getAbsoluteName()]["rpc"])
        rpc = pvaccess.RpcClient(rpcClientAddress)
        request = pvaccess.PvObject({"qualifier": pvaccess.STRING})
        request.set({"qualifier": "seed"})
        response = rpc.invoke(request)
        seed = response["value"]
        return seed

    def loadPlant(self, var, pvObjValue, pvObjValueStructureDict, seed, crc):
        rpcClientAddress = str(self.variableMap[var.getAbsoluteName()]["rpc"])
        rpc = pvaccess.RpcClient(rpcClientAddress)
        request = pvaccess.PvObject({"qualifier": pvaccess.STRING, "hash": pvaccess.UINT, "seed": pvaccess.UINT, "value": pvObjValueStructureDict})
        request.set({"qualifier": "load", "hash": crc, "seed": seed, "value": pvObjValue})
        response = rpc.invoke(request)
        log.debug("For variable {0}, the reply was {1}".format(var.getAbsoluteName(), response))
        ok = (response["status"] == "true")
        return ok

    def loadIntoPlant(self, pageName):
        log.info("Loading {0}".format(pageName)) 
        variablesPlantInfo = self.server.getVariablesInfo(self.pageName, self.variables)
        for var in variablesPlantInfo:
            fullVarName = var.getAbsoluteName()
            ok = (fullVarName in self.variableMap)
            if (not ok):
                log.critical("Variable {0} is not registered".format(fullVarName)) 
            if (ok):
                pvObjValueStructureDict = self.getPVObjectDict(var)
                ok = self.checkPlantStructure(var, pvObjValueStructureDict)
            if (ok):
                seed = self.getPlantSeed(var)
                log.info("For variable {0}, the seed is {1}".format(var.getAbsoluteName(), seed))
                key = int(self.variableMap[var.getAbsoluteName()]["key"])
                keyBin = self.getBinaryValue(key, "uint32")
                seedBin = self.getBinaryValue(seed, "uint32")
                varBinValue = self.getBinary(var, keyBin + seedBin)
                log.debug("[" + binascii.hexlify(varBinValue) + "]")
                crc = self.computeCRC(varBinValue)
                log.info("For variable {0}, the CRC is {1}".format(var.getAbsoluteName(), hex(crc)))
                pvObjValue = self.getPVObjectValue(var)
                log.info("For variable {0}, loading {1}".format(var.getAbsoluteName(), pvObjValue)) 
                ok = self.loadPlant(var, pvObjValue, pvObjValueStructureDict, seed, crc)

        return ok

    def isLoadable(self, pageName):
        return (pageName == self.pageName)

