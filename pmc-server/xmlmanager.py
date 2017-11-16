import logging
#Several workers (i.e. processes) will need to interact with this XmlManager
import multiprocessing
import os
import threading
from xml.etree import cElementTree

log = logging.getLogger("psps-{0}".format(__name__))

class XmlManager(object):
    """ Multi-process and multi-threading safe access to xml file based database.
        The schedules and plant xmls after being parsed are cached in memory with an house-keeping TODO.
    """
    
    def __init__(self, numberOfMultiprocessLocks = 32):
        """ Creates two semaphores which guarantee that only one connection can interact with the same XML file at the same time.
            But also allowing different files to be processed in parallel
        """
        #Disallows multiple connections from updating the same XML file
        self.xmlUpdateGlobalLock = multiprocessing.Lock()
        #Allows to process in parallel schedules with different ids
        self.xmlUpdateManager = multiprocessing.Manager()
        self.xmlUpdateLocks = self.xmlUpdateManager.dict()
        self.openXmls = self.xmlUpdateManager.dict()
        
        #Multiprocessing locks cannot be created and shared in runtime...
        self.multiProcessingLocks = self.xmlUpdateManager.dict()
        self.multiProcessingLocksArr = []
        i = 0
        while (i < numberOfMultiprocessLocks):
            self.multiProcessingLocksArr.append(multiprocessing.Lock())
            i = i + 1

        log.info("Created XmlManager")
        self.xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
                      "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    def getCachedXmlTree(self, xmlPath):
        """ Parses the xml defined by the xmlPath and caches it in memory.
            
            Args:
                xmlPath (str): path to the xml file to be parsed.
            Returns:
                The parsed Xml file or None if an error occurs.
        """
        #TODO must make sure that this has house keeping and that this is cleaned when the user logout
        #Also, the number of opened schedules per user shall be limited
        ret = None
        if (xmlPath not in self.openXmls):
            try:
                self.openXmls[xmlPath] = cElementTree.parse(xmlPath)
                ret = self.openXmls[xmlPath]
            except Exception as e:
                log.critical("Error loading xml file {0}".format(xmlPath))
        return ret

    def acquire(self, xmlPath):
        """ Acquires a multi-processing, multi-threading safe lock access to an xmlPath.
        """
        log.debug("Locking against key {0}".format(xmlPath))
        #Lock for all processes
        self.xmlUpdateGlobalLock.acquire()
        #Then create a process and threading lock for each xmlPath
        xmlPathBeingProcessed = (xmlPath in self.xmlUpdateLocks)
        if (not xmlPathBeingProcessed):
            pid = str(os.getpid())
            if (pid in self.multiProcessingLocks):
                lock = self.multiProcessingLocks[pid]
            else:
                lock = self.multiProcessingLocksArr.pop()
                print lock
                #self.multiProcessingLocks[pid] = lock
            self.xmlUpdateLocks[xmlPath] = {"plock": lock, "tlock": self.xmlUpdateManager.Lock(), "counter": 1}
        else:
            self.xmlUpdateLocks[xmlPath]["counter"] = self.xmlUpdateLocks[xmlPath]["counter"] + 1
        self.xmlUpdateGlobalLock.release()
        self.xmlUpdateLocks[xmlPath]["plock"].acquire()
        self.xmlUpdateLocks[xmlPath]["tlock"].acquire()

    def release(self, xmlPath):
        """ Releases a multi-processing, multi-threading safe lock access to an xmlPath.
        """
        log.debug("Releasing against key {0}".format(xmlPath))
        #Lock for all processes
        self.xmlUpdateGlobalLock.acquire()
        xmlUpdateLocks[xmlPath]["plock"].release()
        xmlUpdateLocks[xmlPath]["tlock"].release()
        self.xmlUpdateGlobalLock.release()

    def closeLock(self, xmlPath):
        """ Close a multi-processing, multi-threading lock that was associated to an xmlPath.
        """
        self.xmlUpdateGlobalLock.acquire()
        if (self.xmlUpdateLocks[xmlPath]["counter"] == 0):
            log.debug("Closing lock {0}".format(xmlPath))
            self.xmlUpdateLocks[xmlPath].pop("plock")
            self.xmlUpdateLocks[xmlPath].pop("tlock")
            self.xmlUpdateLocks.pop(xmlPath)
        self.xmlUpdateGlobalLock.release()

    def getVariableInfo(self, variableName, xmlPath):
        """ Gets all the information (including metadata that is available for a given variable).
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
        Args:
            xmlPath (str): the name of the xml file.
            variableName (str): the variable name (aka identifier).
            plantRootXml (cElementTree node) pointing at the appropriate plant system folder.

        Returns:
            The following information about a given variable:
            - type as one of: uint8, int8, uint16, int16, uint32, int32, uint64, int64, string;
            - numberOfElements: as an array where each entry contains the number of elements on any given direction; 
            - name: the full variable name (containing any structure naming information);
            - variableId: same as name. TODO: deprecate;
            - description: one-line description of the variable;
            - permissions: user groups that are allowed to change this variable;
            - value: string encoded variable value.
        """

        variable = {}
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            #TODO for the time being I will encode the plant system name as the first @ token. This needs discussion at some stage
            idx = variableName.find("@")
            if (idx != -1):
                plantSystemName = variableName[:idx]
                variableName = variableName[idx + 1:]
                path = variableName.split("@")
                
                plantRootXml = xmlRoot.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']/ns0:plantRecords".format(plantSystemName), self.xmlns)
                r = plantRootXml
                for p in path[:-1]:
                    r = r.find("./ns0:folders/ns0:folder[ns0:name='{0}']".format(p), self.xmlns)
                    if (r == None):
                        log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, p))
                        break
                if (r is not None):
                    r = r.find("./ns0:records/ns0:record[ns0:name='{0}']".format(path[-1]), self.xmlns)
                    variable["type"] = self.convertVariableTypeFromXML(r.attrib["{" + ns["xsi"] + "}type"])
                    variable["numberOfElements"] = "[" + r.attrib["size"] + "]"
                    variable["name"] = plantSystemName + "@" + variableName
                    #TODO deprecate variableId
                    variable["variableId"] = variable["name"]
                    variable["description"] = r.find("./ns0:description", self.xmlns).text
                    variable["permissions"] = ["experts-1"]
                    valuesXml = r.findall(".//ns0:value", self.xmlns)
                    values = []
                    for v in valuesXml:
                        values.append(v.text)
                    variable["value"] = values
                    log.debug("Loaded variable {0}".format(variable["name"]))
                else:
                    log.critical("No plant system defined for variable {0}".format(variableId))

        return variable


    def updateVariable(self, variableName, xmlPath, variableValue):
        """ Updates the value of the a variable in a given xml (plant or schedule).
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            Note that this change is not sinked to disk.
    
        Args:
            variableName (str): the name of the variable to update.
            xmlPath (str): the xml to be updated (identified with the path to the original file).
            variableValue (str): the value of the variable to be updated.

        Returns:
            True if the variable is sucessfully updated.
        """

        #Allow only one process to interact with a given xml at the time
        #Makes sure that this is both multi-processing and multi-threading safe
        log.debug("Updating {0} in {1} with value {2}".format(variableName, xmlPath, variableValue))

        ok = False
        #Work on memory as opposed to working on file. TODO this must properly managed so that memory consumption does not ramp to infinity
        #Update the XML
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            root = tree.getroot()
            #TODO for the time being I will encode the plant system name as the first @ token. This needs discussion at some stage
            idx = variableName.find("@")
            if (idx != -1):
                plantSystemName = variableName[:idx]
                variableName = variableName[idx + 1:]
                path = variableName.split("@")
               
                r = root.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']/ns0:plantRecords".format(plantSystemName), self.xmlns)
                for p in path[:-1]:
                    r = r.find("./ns0:folders/ns0:folder[ns0:name='{0}']".format(p), self.xmlns)
                    if (r == None):
                        log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, p))
                        break

                variable = {}
                if (r is not None):
                    r = r.find("./ns0:records/ns0:record[ns0:name='{0}']".format(path[-1]), self.xmlns)
                    #Assume that it is not an array. TODO change ASAP!
                    valueXml = r.find("./ns0:values/ns0:value", self.xmlns)
                    valueXml.text = str(variableValue)
                    ok = True
            else:
                log.critical("No plant system defined for variable {0}".format(variableName))

        return ok

    def getAllVariablesValue(self, xmlPath):
        """ Gets the value for all variables in a given xml file.
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.

        Args:
            The xml containing the variables.

        Returns:
            An array with variable:value pairs.
        """
        variables = []
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            plantRootXml = root.find("./ns0:plantSystems", self.xmlns)
            if (plantRootXml != None):
                for ps in plantRootXml:
                    plantSystemNameXml = r.find("./ns0:name", self.xmlns)
                    if (plantSystemNameXml != None):
                        plantSystemName = plantSystemNameXml.text
                        plantRecordsXml = ps.find("./ns0:plantRecords", self.xmlns)
                        for pr in plantRecordsXml:
                            records = pr.findall(".//ns0:record", self.xmlns)
                            for r in records:
                                recordNameXml = r.find("./ns0:name", self.xmlns)
                                if (recordNameXml != None):
                                    vp = {
                                        "variable": plantSystemName + "@" + recordNameXml.text,
                                        "value": []
                                    } 
                                    valuesXml = r.findall(".//ns0:value", self.xmlns)
                                    values = []
                                    for v in valuesXml:
                                        values.append(v.text)
                                    vp["value"] = values
                                    variables.append(vp)
                                else:
                                    log.critical("No record name defined in {0}".format(xmlPath))
                    else:
                        log.critical("No plantSystem name defined in {0}".format(xmlPath))
            else:
                log.critical("No plantSystems defined in {0}".format(xmlPath))

        return variables

    def getVariableValue(self, variableName, xmlPath):
        """ Gets the value for a given variable in a given xml file.
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.

        Args:
            The xml containing the variables.

        Returns:
            An array with the value of the variable.
        """

        value = []
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            #TODO for the time being I will encode the plant system name as the first @ token. This needs discussion at some stage
            idx = variableName.find("@")
            if (idx != -1):
                plantSystemName = variableName[:idx]
                variableName = variableName[idx + 1:]
                path = variableName.split("@")
                plantRootXml = xmlRoot.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']/ns0:plantRecords".format(plantSystemName), self.xmlns)
                r = plantRootXml
                for p in path[:-1]:
                    r = r.find("./ns0:folders/ns0:folder[ns0:name='{0}']".format(p), self.xmlns)
                    if (r == None):
                        log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, p))
                        break
                if (r is not None):
                    r = r.find("./ns0:records/ns0:record[ns0:name='{0}']".format(path[-1]), self.xmlns)
                    for v in valuesXml:
                        value.append(v.text)
            else:
                log.critical("No plant system defined for variable {0}".format(variableId))

        return value

 
    def __str__(self):
        """Returns a list of all the currently open xml files.
        """
        return str(self.xmlScheduleUpdateLocks.values())
