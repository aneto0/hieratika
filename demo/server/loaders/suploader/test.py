import binascii
import crcmod
import pvaccess
import struct

def ComputeCRC(pol, data):
    crc32Fun = crcmod.mkCrcFun(0x100000000 + pol, initCrc=0, xorOut=0xFFFFFFFF)
    print len(data)
    print "[" + binascii.hexlify(data) + "]"
    return crc32Fun(data)

def GetBinaryValue(val, pvaType):
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
        print "Unrecognised type"
    ret = struct.pack(t, val)
    return ret

def GetBinaryImage(responseValue, responseValueStruct):
    ret = ""
    for k,v in responseValue.items():        
        if isinstance(v, dict):
            ret += GetBinaryImage(v, responseValueStruct[k])
        if isinstance(v, list):
            for l in v:
                ret += GetBinaryValue(l, responseValueStruct[k])
        else: 
            ret += GetBinaryValue(v, responseValueStruct[k])

    print ret
    return ret

rpc = pvaccess.RpcClient("55a0::Cfg::Interface2")
request = pvaccess.PvObject({"qualifier": pvaccess.STRING})
request.set({"qualifier": "seed"})
print request
response = rpc.invoke(request)
print response
seed = response["value"]

request.set({"qualifier": "read"})
print request
response = rpc.invoke(request)
print "@@@@@@@@@@@@@"
print response.getPyObject("value")
responseValue = response["value"]
print "@@@@@@@@@@@@@"
print response
print responseValue
print "@@@@@@@@@@@@@"

structureResponse = response.getStructureDict()
print structureResponse
structureResponseValue = structureResponse["value"]
currentStruct = pvaccess.PvObject(structureResponseValue)
print "@@@@@@@@@@@@@"
print "@@@@@@@@@@@@@"
print "@@@@@@@@@@@@@"
print currentStruct
print "@@@@@@@@@@@@@"
print "@@@@@@@@@@@@@"
print "@@@@@@@@@@@@@"
request = pvaccess.PvObject({"qualifier": pvaccess.STRING, "value": currentStruct})

responseValue["WOTime"] = 0
memory = GetBinaryValue(seed, pvaccess.ScalarType.ULONG)
memory += GetBinaryImage(responseValue, structureResponseValue)
crc = ComputeCRC(12345678, memory)
print hex(crc)

responseValue["WOTime"] = 5
memory = GetBinaryValue(seed, pvaccess.ScalarType.ULONG)
memory += GetBinaryImage(responseValue, structureResponseValue)
crc = ComputeCRC(12345678, memory)
print hex(crc)

request = pvaccess.PvObject({"qualifier": pvaccess.STRING, "hash": pvaccess.ULONG, "value": currentStruct})
request.set({"qualifier": "load", "hash": crc, "value": responseValue})
print request
response = rpc.invoke(request)
print response

