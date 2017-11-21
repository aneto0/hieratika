
##
# Standard imports
##
import fnmatch
import logging
import multiprocessing
import os
import time
import timeit
from xml.etree import cElementTree
from xml.dom import minidom

##
# Project imports
##
from scriptorium.server import ScriptoriumServer
from scriptorium.page import Page
from scriptorium.schedule import Schedule
from scriptorium.user import User
from scriptorium.usergroup import UserGroup 
from scriptorium.util.lockpool import LockPool

##
# Global definitions
##
log = logging.getLogger("{0}".format(__name__))

class PSPSServer(ScriptoriumServer):
    """ Access must be multiprocess and multithread safe.
    """

    #XML namespaces
    xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
             "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    def __init__(self):
        self.xmlIds = {}
        manager = multiprocessing.Manager()
        #Must be multiprocessing safe
        self.users = manager.list()
        self.pages = manager.list()
        self.tokens = manager.dict()
        self.openXmls = {}

    def authenticate(self, username):
        #TODO
        return True

    def load(self, config):
        ok = True
        try:
            numberOfLocks = int(config["numberOfLocks"])
            usersXmlFilePath = config["usersXmlFilePath"]
            pagesXmlFilePath = config["pagesXmlFilePath"]
            self.baseDir = config["baseDir"]
            self.lockPool = LockPool(numberOfLocks)
        except KeyError as e:
            log.critical(str(e))
            ok = False 
    
        if (ok):
            ok = self.loadUsers(usersXmlFilePath)

        if (ok):
            ok = self.loadPages(pagesXmlFilePath)

        return ok

    def getXmlId(self, xmlPath):
        """ TODO doc. Needed to have smaller keys
        """
        #TODO housekeeping
        try:
            ret = self.xmlIds[xmlPath]
        except KeyError:
            ret = str(time.time())
            self.xmlIds[xmlPath] = ret
        return ret
        
    def getPlantInfo(self, pageName, requestedVariables):
        xmlFileLocation = "{0}/psps/configurations/{1}/000/plant.xml".format(self.baseDir, pageName)
        log.debug("Loading plant configuration from {0}".format(xmlFileLocation))
        perfStartTime = timeit.default_timer()
        variables = []
        xmlId = self.getXmlId(xmlFileLocation)
        self.lockPool.acquire(xmlId)
        for variableName in requestedVariables:
            variable = self.getVariableInfo(variableName, xmlFileLocation)
            if (variable is not None):
                variables.append(variable) 
            
        self.lockPool.release(xmlId)
        perfElapsedTime = timeit.default_timer() - perfStartTime
        log.debug("Took {0} s to get the information for all the {1} variables in the plant for page {2}".format(perfElapsedTime, len(requestedVariables), pageName))
        return variables 

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
                if (r is not None):
                    for p in path[:-1]:
                        r = r.find("./ns0:folders/ns0:folder[ns0:name='{0}']".format(p), self.xmlns)
                        if (r is None):
                            log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, p))
                            break
                    if (r is not None):
                        r = r.find("./ns0:records/ns0:record[ns0:name='{0}']".format(path[-1]), self.xmlns)
                        variable["type"] = self.convertVariableTypeFromXML(r.attrib["{" + self.xmlns["xsi"] + "}type"])
                        variable["numberOfElements"] = "[" + r.attrib["size"] + "]"
                        variable["name"] = plantSystemName + "@" + variableName
                        #TODO deprecate variableId
                        variable["variableId"] = variable["name"]
                        variable["description"] = r.find("./ns0:description", self.xmlns).text
                        variable["permissions"] = ["experts-1"]
                        valuesXml = r.findall("./ns0:value", self.xmlns)
                        values = []
                        for v in valuesXml:
                            values.append(v.text)
                        variable["value"] = values
                        log.debug("Loaded variable {0}".format(variable["name"]))
                    else:
                        log.critical("No record defined for variable {0}".format(variableName))
                else:
                    log.critical("No plant system defined for variable {0}".format(plantSystemName + "@" + variableName))

        return variable

    def getUser(self, username):
        user = None
        idx = self.users.index(username)
        if (idx >= 0):
            user = self.users[idx]
        return user

    def getUsers(self):
        return self.users

    def getPages(self):
        return self.pages

    def getPage(self, pageName):
        page = None
        idx = self.pages.index(pageName)
        if (idx >= 0):
            page = self.pages[idx]
        return page

    def getSchedules(self, username, pageName):
        schedules = []
        allSchedulesXML = self.getAllFiles(username, pageName)

        for xmlFile in allSchedulesXML:
            description = ""
            xmlId = self.getXmlId(xmlFile)
            self.lockPool.acquire(xmlId)
            tree = self.getCachedXmlTree(xmlFile)
            if (tree is not None):
                xmlRoot = tree.getroot()
                description = xmlRoot.find("./ns0:description", self.xmlns)
                if (description is not None):
                    description = description.text
            self.lockPool.release(xmlId)
            filePath = xmlFile.split("/")
            schedule = Schedule(xmlFile, filePath[-1], pageName, username, description)
            schedules.append(schedule);

        return schedules

    def getSchedule(self, scheduleName):
        """ TODO define schedule structure

        Args:
            scheduleName (str): unique schedule identifier.
        Returns:
            Information about the requested schedule.
        """
        pass

    def getScheduleVariablesValues(self, scheduleUID):
        xmlId = self.getXmlId(scheduleUID)
        self.lockPool.acquire(xmlId)
        variables = self.getAllVariablesValues(scheduleUID)
        self.lockPool.release(xmlId)
        return variables

    def updateSchedule(self, tid, scheduleName, variables):
        updatedVariables = []
        xmlId = getXmlId(scheduleName)
        self.lockPool.acquire(xmlId)
        for v in variables:
            variableId = v["id"]
            value = v["value"]
            if(updateVariable(variableName, scheduleName, variableValue)):
                updatedVariables["variables"].append({"variableId" : variableId, "value" : value})
        self.lockPool.release(xmlId)
        return updatedVariables 

    def updatePlant(self, variables):
        """TODO
        """
        return False

    def createSchedule(self, name, description, username, pageName):
        """ Creates a new schedule. TODO
        """
        pass

    def convertVariableTypeFromXML(self, xmlVariableType):
        #TODO move to helper module
        toReturn = "string"
        if (xmlVariableType == "recordDouble"):
            toReturn = "float64" 
        elif (xmlVariableType == "recordFloat"):
            toReturn = "float32" 
        elif (xmlVariableType == "recordString"):
            toReturn = "string" 
        return toReturn

    def getAllFiles(self, username, pageName):
        """ TODO
        """
        matches = []
        directory = "{0}/users/{1}/configurations/{2}".format(self.baseDir, username, pageName)
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.xml'):
                if (filename != "plant.xml"):
                    matches.append(os.path.join(root, filename))
        return matches

    def loadUsers(self, userXml):
        """Loads a list of users from an xml file.
           Args:
               userXml (string): path to the file which contains the user definitions.

           Returns:
               True if the file can be sucessfully loaded.
        """
        ok = True
        log.info("Loading xml: {0}".format(userXml))
        try:
            root = cElementTree.parse(userXml)
            #Get all users
            usersXml = root.findall(".//ns0:user", self.xmlns)
            for userXml in usersXml:
                groups = []
                #For each user load the groups
                groupsXml = userXml.findall("./ns0:group", self.xmlns)
                for groupXml in groupsXml:
                    groupNameXml= groupXml.find("./ns0:name", self.xmlns)
                    groups.append(UserGroup(groupNameXml.text)) 

                usernameXml = userXml.find("./ns0:name", self.xmlns)
                user = User(usernameXml.text, groups) 
                self.users.append(user)
                log.info("Registered user: {0}".format(user))
        except Exception as e:
            log.critical("Error loading xml file {0} : {1}".format(userXml, str(e)))
            ok = False 

        return ok

    def loadPages(self, pagesXmlFilePath):
        """Loads a list of pages from an xml file.
           Args:
               pageXml (string): path to the file which contains the page definitions.

           Returns:
               True if the file can be sucessfully loaded.
        """
        ok = True
        log.info("Loading xml: {0}".format(pagesXmlFilePath))
        try:
            root = cElementTree.parse(pagesXmlFilePath)
            #Get all pages
            pagesXml = root.findall(".//ns0:page", self.xmlns)
            for pageXml in pagesXml:
                pageName = pageXml.find("./ns0:name", self.xmlns).text
                pageUrl = pageXml.find("./ns0:url", self.xmlns).text
                pageDescription = pageXml.find("./ns0:description", self.xmlns).text
                page = Page(pageName, pageUrl, pageDescription)
                self.pages.append(page) 

                log.info("Registered page: {0}".format(page))
        except Exception as e:
            log.critical("Error loading xml file {0} : {1}".format(pageXml, str(e)))
            ok = False 

        return ok

    def getCachedXmlTree(self, xmlPath):
        """ Parses the xml defined by the xmlPath and caches it in memory.
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            
            Args:
                xmlPath (str): path to the xml file to be parsed.
            Returns:
                The parsed Xml file or None if an error occurs.
        """
        #TODO must make sure that this has house keeping and that this is cleaned when the user logout
        #Also, the number of opened schedules per user shall be limited
        xmlId = self.getXmlId(xmlPath)
        try:
            ret = self.openXmls[xmlPath]
        except Exception as e:
            try:
                self.openXmls[xmlPath] = cElementTree.parse(xmlPath)
                ret = self.openXmls[xmlPath]
            except Exception as e:
                log.critical("Error loading xml file {0}: {1}".format(xmlPath, str(e)))
                ret = None
        return ret

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

    def getVariableValue(self, r, variableName, variables):
        """ Recursively gets all the variable values for a given plantSystem node in the xml.
            
            Args:
                r (xmlElement): walks the xml Tree. The first time this function is called it shall point at the plantRecords.
                variableName (str): the name of the variable. It is constructed as the function recursively walks the tree. The separator is the @ symbol.
                variables (__dict__): dictionary where the value of the variable is stored.
        """
        records = r.find("./ns0:records", self.xmlns)
        if (records is None):
            r = r.find("./ns0:folders", self.xmlns)
            if (r is None):
                log.critical("Wrong xml structure. ns0:folders is missing")
                return None
            else:
                folders = r.findall("./ns0:folder", self.xmlns)
                variableNameBeforeFolders = variableName
                for f in folders:
                    n = f.find("./ns0:name")
                    if (n is not None):
                        variableName = variableNameBeforeFolders + "@" + n.text
                        self.getVariableValueR(f, variableName, variables)
                    else:
                        log.critical("Wrong xml structure. ns0:name is missing in folder")
        else:
            records = records.findall("./ns0:record", self.xmlns)
            variableNameBeforeRecord = variableName
            for rec in records:
                n = rec.find("./ns0:name")
                if (n is not None):
                    variableName = variableNameBeforeRecord + "@" + n.text
                    valuesXml = rec.find("./ns0:values", self.xmlns)
                    if (valuesXml is not None):
                        valueXml = valuesXml.findall("./ns0:value", self.xmlns)
                        values = []
                        for v in valueXml:
                            values.append(v.text)
                        variables[variableName] = values
                else:
                    log.critical("Wrong xml structure. ns0:name is missing in record")
                log.debug("Retrieved value for variable [{0}]".format(variableName))

    def getAllVariablesValues(self, xmlPath):
        variables = {}
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            #TODO for the time being I will encode the plant system name as the first @ token. This needs discussion at some stage
            #For every plant system
            plantSystemsRootXml = xmlRoot.findall(".//ns0:plantSystem", self.xmlns)
            for plantSystemXml in plantSystemsRootXml:
                plantSystemName = plantSystemXml.find("./ns0:name", self.xmlns).text
                plantRecordsXml = plantSystemXml.find("./ns0:plantRecords", self.xmlns)
                self.getVariableValueR(plantRecordsXml, plantSystemName, variables)
        return variables


