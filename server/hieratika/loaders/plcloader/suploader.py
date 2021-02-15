from pvaccess import *
import struct
from collections import OrderedDict
import numpy as np
import json
from ctypes import *

shared_object = "/home/codac-dev/hieratika/server/hieratika/loaders/plcloader/crc.so"
crc_helper = CDLL(shared_object)

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
    seed_bytes = struct.pack('<B', seed)
    s1 = np.asarray(struct.unpack('<B',b'seed_bytes[0]'))
    s2 = np.asarray(struct.unpack('<B',seed_bytes[1]))
    s3 = np.asarray(struct.unpack('<B',seed_bytes[2]))
    s4 = np.asarray(struct.unpack('<B',seed_bytes[3]))

    if seed != 0:
        checksum = table[(checksum ^ s1[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s2[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s3[0]) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ s4[0]) & 0xFF] ^ (checksum >> 8)

    for index in range(3213):
        checksum = table[(checksum ^ cfg_list[index]['ID']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Data_L']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Data_M']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Address_L']) & 0xFF] ^ (checksum >> 8)
        checksum = table[(checksum ^ cfg_list[index]['Address_M']) & 0xFF] ^ (checksum >> 8)

    checksum = checksum ^ 0xFFFFFFFF

    checksum = checksum % (1<<32) #convert to unsigned 32

    return crc

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
with open('../../../config.json') as json_cfg:
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

print(j)
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
