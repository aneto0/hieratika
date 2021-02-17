from pvaccess import *
import struct
from collections import OrderedDict
import numpy as np
import json
from ctypes import *

shared_object = "/home/codac-dev/hieratika/server/hieratika/loaders/plcloader/crc.so"
crc_helper = CDLL(shared_object)

def sendToSup():
    #Setting up RPCClient
    rpc = RpcClient('55a0::Cfg::Interface')
    rpc.setTimeout(30.0)
    
    #Reading configuration
    readRequest = PvObject({'qualifier' : STRING})
    readRequest.setString('qualifier', 'read')
    print("INFO PLCLoader -- Reading configuration...")
    readResponse = rpc.invoke(readRequest)
    status = readResponse.getBoolean('status')
    if status != True:
        print("...failure")
    else:
        print("...success")
    
    #Initialisation
    #Retrieving first the seed
    status = None
    initRequest = PvObject({'qualifier' : STRING})
    initRequest.setString('qualifier', 'init')
    print("INFO PLCLoader -- Retrieving seed...")
    initResponse = rpc.invoke(initRequest)
    status = initResponse.getBoolean('status')
    if status != True:
        print("...failure")
    else:
        print("...success")
    
    seed = initResponse.getUInt('value')
    print("...",seed,"...")
    
    #Initialise table for checksum
    #table = [None] * 256
    poly = 0xEDB88320
    #table_init = False
    #InitTable(table, poly, table_init)
    
    
    
    #Loading configuration
    loadRequest = PvObject({'qualifier' : STRING, 'seed' : UINT, 'hash' : UINT, 'value' : [{'ID' : UBYTE, 'Data_L' : UBYTE, 'Data_M' : UBYTE, 'Address_L' : UBYTE, 'Address_M' : UBYTE}]})
    loadRequest.setString('qualifier', 'load')
    cfg_list = readResponse.getStructureArray('value')
    
    size = 0
    with open('config.json') as json_cfg:
        data = json.load(json_cfg)
        i = 0
        for p in data:
            cfg_list[i]['ID'] = p['ID']
            cfg_list[i]['Data_L'] = p['Data_L']
            cfg_list[i]['Data_M'] = p['Data_M']
            cfg_list[i]['Address_L'] = p['Address_L']
            cfg_list[i]['Address_M'] = p['Address_M']
            i = i + 1
        size = i
    
    data_arr = (c_ubyte * (size*5))(*range(size*5))
    
    j = 0
    k = 0
    for d in cfg_list:
        data_arr[j] = cfg_list[k]['ID']
        j = j + 1
        data_arr[j] = cfg_list[k]['Data_L']
        j = j + 1
        data_arr[j] = cfg_list[k]['Data_M']
        j = j + 1
        data_arr[j] = cfg_list[k]['Address_L']
        j = j + 1
        data_arr[j] = cfg_list[k]['Address_M']
        j = j + 1
        k = k + 1
    
    size = j
    
    loadRequest.setStructureArray('value',cfg_list)
    
    #Compute checksum
    crc = None
    print("INFO PLCLoader -- Computing checksum...")
    #crc = ComputeChecksum(cfg_list, seed, crc)
    crc = crc_helper.CyclicRedundancyCheck(poly, byref(data_arr), size, seed)
    
    if crc < 0:
        crc = crc + 2**32
    
    print("...",crc,"...")
    
    loadRequest.setUInt('seed', seed)
    loadRequest.setUInt('hash', crc)
    print(type(loadRequest['value']))
    print("INFO PLCLoader -- Loading configuration...")
    loadResponse = rpc.invoke(loadRequest)
    status = loadResponse.getBoolean('status')
    if status != True:
        print("...failure")
    else:
        print("...success")

    return status
