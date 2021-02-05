#!/usr/bin/env python
##
# Standard imports
##

from __future__ import absolute_import
from __future__ import print_function
import logging  # For Logging interface
import pvaccess # For pvAccess
import os       # For file path handling routines

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
    print(("obj.%s = %s" % (attr, getattr(obj, attr))))

def extractWriteDataSourcesPath(configFile):
    """ Looks for a defined CVVF DataSources XML definition file to be used when writing to the plant system 
        interface (e.g. Channel Access PVs).

        In the example below, replace <...> as follows: 
            - every <config_variable_name> should be match a configuration object variable.
            - every <plantsystem_variable_name> should map to an EPICS CA process variable
            - every <file_variable_name> should map to a variable in the XML file
                Note: the XML file will be created if it does not already exist.

    Args:
        The fully qualified path to the reference configuration file
    Returns:
        The absolute filename of a CVVF DataSources definition file (see example).

Example:

<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<dataSources>
    <dataSource>
        <engineXml file="data_file.xml"/>
        <variables>
            <variable name="<config_variable_name>" alias="<file_variable_name>"/>
            ...
        </variables>
    </dataSource>
    <dataSource>
        <engineEpics communicationTimeout="100"/>
        <variables>
            <variable name="<config_variable_name>" alias="<plantsystem_variable_name>"/>
            ...
        </variables>
    </dataSource>
</dataSources>
    """
    configDir = os.path.dirname(configFile)
    dataSourceFile = os.path.join(configDir, "WriteDataSources.xml") 
    print(dataSourceFile)
    return dataSourceFile

def apply(fileName):
    log.info("SupClient:apply %s" % fileName)
    # PV Access client
    # This service name should be configurable. Also defined in environment variable SUP_CONFIG_SERVICE
    rpc = pvaccess.RpcClient('CTRL-SUP-CFG:CONFIG')
    
    commands=[]
    # Specify the configuration file name (fully qualified path)
    commands.append("config="+fileName)

    # Only use "WriteDataSources=auto" if the WriteDataSources.xml file does not exist
    config_path = extractWriteDataSourcesPath(fileName)
    if (os.path.isfile(config_path)):
        log.info("DataSourceFile found: %s" % config_path)
        commands.append("WriteDataSourcesAdd="+config_path)
    else:
        log.info("No DataSourceFile found [%s], auto-generating" % config_path)
        commands.append("WriteDataSources=auto")

    # Apply the configuration
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
        print("Failed! "+e.message)

test()
