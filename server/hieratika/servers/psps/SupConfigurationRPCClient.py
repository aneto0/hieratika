#!/usr/bin/env python
##
# Standard imports
##

import logging
import pvaccess 

##
# Logger configuration
##
import logging, logging.handlers, sys
log = logging.getLogger("{0}".format(__name__))

def setupLogging():
    log.setLevel(logging.INFO)
    std_formatter = logging.Formatter("%(levelname)s:{0}:%(module)s.%(funcName)s line %(lineno)d: %(message)s")
    stdout_handler = logging.StreamHandler(sys.stdout)
    #stdout_handler.addFilter(stdout_filter)
    stdout_handler.setFormatter(std_formatter)
    log.addHandler(stdout_handler)

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %s" % (attr, getattr(obj, attr)))

def apply(fileName):
    log.info("SupClient:apply %s" % fileName)
    # PV Access client
    rpc = pvaccess.RpcClient('CTRL-SUP-CFG:CONFIG')
    
    commands=[]
    commands.append("config="+fileName)
    commands.append("WriteDataSources=auto")
    commands.append("Apply")

    request = pvaccess.PvObject({'commands': [pvaccess.STRING]})
    request.set({'commands': commands})
    log.info("RPC request: %s" % request)
    response = rpc.invoke(request)
    log.info("RPC response: %s" % response)

def test():
    try:
        setupLogging()
        apply("/home/codac-dev/psps/configuration/Psps-dummy2/000/plant.xml")
    except pvaccess.PvaException as e:
        print "Failed! "+e.message

#test()
