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
__date__ = "17/11/2017"

##
# Standard imports
##
import ast
import ConfigParser
import errno
import fnmatch
import json
import logging
import os
import shutil
import time
import timeit
import threading
#from xml.etree import cElementTree
#xml.etree cElementTree does not support reverse for parents of a given node
from lxml import etree

##
# Project imports
##
from hieratika.hlibrary import HLibrary
from hieratika.page import Page
from hieratika.schedule import Schedule
from hieratika.server import HieratikaServer
from hieratika.util.lockpool import LockPool
from hieratika.variable import Variable
from hieratika.variableenum import VariableEnum
from hieratika.variablelibrary import VariableLibrary

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class PSPSServer(HieratikaServer):
    """ Access must be multiprocess and multithread safe.
    """

    #Xml namespaces
    xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
             "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    def __init__(self):
        super(PSPSServer, self).__init__()
        self.xmlIds = {}
        #cachedXmls is local to each process since the xml Element cannot be pickled by the multiprocessing Manager
        self.cachedXmls = {}
        self.recordTag = "{{{0}}}record".format(self.xmlns["ns0"])

    def load(self, manager, config):
        ok = True
        try:
            self.pages = manager.list()
            self.structSeparator = config.get("hieratika", "structSeparator") 
            self.standalone = config.getboolean("hieratika", "standalone")
            self.pagesFolder = config.get("hieratika", "pagesFolder")
            numberOfLocks = config.getint("server-impl", "numberOfLocks")
            self.maxXmlIds = config.getint("server-impl", "maxXmlIds")
            self.maxXmlCachedTrees = config.getint("server-impl", "maxXmlCachedTrees")
            self.baseDir = config.get("server-impl", "baseDir")
            self.autoCreatePages = config.getboolean("server-impl", "autoCreatePages")
            self.defaultExperts = ast.literal_eval(config.get("server-impl", "defaultExperts"))
            self.lockPool = LockPool(numberOfLocks, manager)
            #This is to protect the local resources cachedXmls and xmlIds (which are local to the process)
            self.mux = threading.Lock() 
            self.loadPages()
        except (ConfigParser.Error, KeyError) as e:
            log.critical(str(e))
            ok = False 
    
        return ok

    def getXmlId(self, xmlPath):
        """ Creates a unique key and associates it to an xml file path. (needed to have shorter keys as path may potentially be very long).
            Args:
                xmlPath(str): path to the xml file.
            Returns:
                A key which univocally identifies this xml path. 
        """
        self.mux.acquire()
        if (len(self.xmlIds) > self.maxXmlIds):
            log.info("Reached maximum number of cached xmlIds :{0}".format(self.maxXmlIds))
            keys = self.xmlIds.keys()
            for k in keys:
                if (not self.lockPool.isKeyInUse(self.xmlIds[k])):
                    del(self.xmlIds[k])
            log.info("After cleaning the number of cached xmlIds is {0}".format(len(self.xmlIds)))

        try:
            ret = self.xmlIds[xmlPath]
        except KeyError:
            ret = str(time.time())
            self.xmlIds[xmlPath] = ret
        self.mux.release()
        return ret

    def findVariableInXml(self, xmlRoot, variableName):       
        """ Walks the xml tree and finds a given variable.
            Args:
                xmlRoot (xmlElement): xml element pointing at the root of the psps file.
            Returns:
                An xmlElement poiting at the variable identified by variableName (using the structSeparator symbol as a separator for folders).
        """
        idx = variableName.find(self.structSeparator)
        if (idx != -1):
            plantSystemName = variableName[:idx]
            variableName = variableName[idx + 1:]
            path = variableName.split(self.structSeparator)
        else:
            plantSystemName = variableName
            path = []
           
        plantRootXml = xmlRoot.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']".format(plantSystemName), self.xmlns)
        if (plantRootXml is not None):
            r = plantRootXml
            #Skip the plantRecords (iff the length of the path is > 0 since I might need to read the name and the description before plantRecords)
            if (len(path) > 0):
                pr = r.find("./ns0:plantRecords", self.xmlns)
                if (pr is not None):
                    r = pr
            for i, p in enumerate(path):
                memberFound = False
                #Check if it is pointing at records
                records = r.find("./ns0:records", self.xmlns)
                if (not self.containsRecords(records)):
                    #Then must have a folder with this member name
                    r = r.find("./ns0:folders", self.xmlns)
                    if (r is None):
                        log.critical("Wrong xml structure. ns0:folders is missing")
                        return None
                    else:
                        folders = r.findall("./ns0:folder", self.xmlns)
                        for f in folders:
                            n = f.find("./ns0:name", self.xmlns)
                            if (n is not None):
                                folderName = n.text
                                if (folderName == p):
                                    #Found the folder with this member name. Continue.
                                    r = f
                                    memberFound = True
                                    break
                            else:
                                log.critical("Wrong xml structure. ns0:name is missing in folder")
                else:
                    #Reached a record. This must the last name of the variable!
                    if (i != (len(path) - 1)):
                        log.critical("Wrong xml structure. ns0:records were not expected at this location for variable {0}".format(variableName))
                        return None
                    records = records.findall("./ns0:record", self.xmlns)
                    for rec in records:
                        n = rec.find("./ns0:name")
                        if (n is not None):
                            recordName = n.text
                            if (p == recordName):
                                r = rec
                                memberFound = True
                                break
                        else:
                            log.critical("Wrong xml structure. ns0:name is missing in record")
                if (not memberFound):
                    log.critical("Could not find member {0} for variable {1}".format(p, variableName))
        return r


    def createVariableFromRecord(self, rec):
        """ Helper function to create a Variable from a psps record.
            Args:
                rec (xmlElement): xml Element pointing at ns0:record.
            Returns:
                A Variable constructed from the ns0:record elements
        """
        try:
            nameXml = rec.find("./ns0:name", self.xmlns)
            aliasXml = rec.find("./ns0:alias", self.xmlns)
            typeFromXml = self.convertVariableTypeFromXml(rec.attrib["{" + self.xmlns["xsi"] + "}type"])
            descriptionXml = rec.find("./ns0:description", self.xmlns)
            value = []
            valuesXml = rec.find("./ns0:values", self.xmlns)
            if (valuesXml is not None):
                #len(allValuesXml) > 1 should only happen the first time a plant/schedule is read (since the current version of the psps editor stores arrays as lists of <value></value>. In the future these lists should be deprecated. I always serialize the values in a single <value>[]</value> element when I update the plant/schedule.
                allValuesXml = valuesXml.findall("./ns0:value", self.xmlns)
                for valueXml in allValuesXml:
                    try:
                        #In order to be able to trap the case where there are strings
                        val = json.loads(valueXml.text)
                    except Exception as e:
                        val = valueXml.text
                        log.critical("Failed to load json {0}. Returning the original text.".format(e))
                    if (isinstance(val, list)):
                        if (len(value) == 0):
                            value = val
                        else:
                            value.append(val)
                    else:
                        value.append(val)
            else:
                log.critical("./ns0:values is missing for record with name {0}".format(nameXml.text))

            numberOfElements = ast.literal_eval(rec.attrib["size"])
            #TODO handle permissions in xml (currently only the default ones are supported)
            if (typeFromXml == "enum"):
                choicesXml = rec.find("./ns0:choices", self.xmlns)
                if (choicesXml is not None):
                    choicesXml = choicesXml.findall("./ns0:choice", self.xmlns)
                    choices = []
                    for choiceXml in choicesXml:
                        choices.append(choiceXml.text)
                    variable = VariableEnum(nameXml.text, aliasXml.text, descriptionXml.text, typeFromXml, self.defaultExperts, numberOfElements, value, [], choices)
                    log.debug("Added {0} choices for {1}".format(choices, variable.getName()))
                else:
                    log.critical("Could not find ns0:choices for {0}".format(nameXml.text))
            elif (typeFromXml == "library"):
                libraryXml = rec.find("./ns0:library", self.xmlns)
                if (libraryXml is not None):
                    libraryNameXml = libraryXml.find("./ns0:name", self.xmlns)
                    if (libraryNameXml is not None):
                        libraryName = libraryNameXml.text
                        mappingsXml = libraryXml.find("./ns0:mappings", self.xmlns)
                        mappings = []
                        if (mappingsXml is not None):
                            mapsXml = mappingsXml.findall("./ns0:map", self.xmlns)
                            for mapXml in mapsXml:
                                mapSourceXml = mapXml.find("./ns0:source", self.xmlns)
                                mapDestinationXml = mapXml.find("./ns0:destination", self.xmlns)
                                if ((mapSourceXml is not None) and (mapDestinationXml is not None)):
                                    mappings.append((mapSourceXml.text, mapDestinationXml.text))
                                else:
                                    log.critical("Could not find ns0:source or ns0:destination mappings for {0}".format(nameXml.text))
                        else:
                            log.critical("Could not find ns0:library mappings for {0}".format(nameXml.text))
                    else:
                        log.critical("Could not find ns0:library name for {0}".format(nameXml.text))
                    variable = VariableLibrary(nameXml.text, aliasXml.text, descriptionXml.text, typeFromXml, self.defaultExperts, numberOfElements, value, libraryName, mappings)
                    log.debug("Added {0} mappings for {1}".format(mappings, variable.getName()))
                else:
                    log.critical("Could not find ns0:library for {0}".format(nameXml.text))
            else:
                variable = Variable(nameXml.text, aliasXml.text, descriptionXml.text, typeFromXml, self.defaultExperts, numberOfElements, value)
            log.debug("Loaded {0}".format(variable))
        except Exception as e:
            #Not very elegant to catch all the possible exceptions...
            if (nameXml is None):
                log.critical("Wrong xml structure. {0}".format(e))
            else:
                log.critical("Wrong xml structure for record with name {0}. {1}".format(nameXml.text, e))

            variable = None
        return variable

    def getVariableInfo(self, r, parent):
        """ Recursively gets all the variable information, including information of any member variables.
            
            Args:
                r (xmlElement): points at the current the xml Element in the tree. 
                parent (Variable): the Variable to which this variable should be added as a member.

            Returns:
                The fully populated (including any member substructures) parent Variable.
        """
        #At this point the xml can only be pointing at a set of records or at a list of folders (the case where it is pointing at the record must be trapped before)
        records = r.find("./ns0:records", self.xmlns)
        if (not self.containsRecords(records)):
            r = r.find("./ns0:folders", self.xmlns)
            if (r is not None):
                folders = r.findall("./ns0:folder", self.xmlns)
                for f in folders:
                    n = f.find("./ns0:name", self.xmlns)
                    if (n is not None):
                        member = Variable(n.text, n.text)
                        parent.addMember(member)
                        self.getVariableInfo(f, member)
                    else:
                        log.critical("Wrong xml structure. ns0:name is missing in folder")
            else:
                log.critical("Wrong xml structure. ns0:folders is missing in folder")
        else:
            records = records.findall("./ns0:record", self.xmlns)
            for rec in records:
                member = self.createVariableFromRecord(rec) 
                if (member is not None):
                    if (parent is None):
                        parent = member
                    else:
                        parent.addMember(member)
                else:
                    return None
        return parent

    def getAbsoluteVariableName(self, xmlRoot, fullVarName):
        """ 
        Returns:
            The absolute variable name with-in the scope of a structure.
        """
        r = xmlRoot.find(".//ns0:record[ns0:name='{0}']".format(fullVarName), self.xmlns)
        configurationContainerFullPath = "{{{0}}}configurationContainer".format(self.xmlns["ns0"])

        #Note that iterancestors is an lxml function
        for a in r.iterancestors():
            n = a.find("./ns0:name", self.xmlns)
            if (a.tag != configurationContainerFullPath):
                if n is not None:
                    fullVarName = n.text + self.structSeparator + fullVarName

        return fullVarName

    def loadConstraints(self, xmlRoot):
        """ Loads all the constraints defined in the xml file and (if needed) resets all the variables names to the full structured path name.
        Args:
            xmlRoot (Element): pointing at the root of the xml file where to load the constraints from.
        Returns:
            A dictionary with {key:[functions], ...}, where key is the variable id and functions are the functions where this variable is an argument.
        """
        log.debug("Loading constraints")
        constraints = {}
        plantSystemsRootXml = xmlRoot.findall(".//ns0:plantSystem", self.xmlns)
        for plantSystemXml in plantSystemsRootXml:
            plantSystemName = plantSystemXml.find("./ns0:name", self.xmlns).text
            log.debug("Getting constraints for plant system {0}".format(plantSystemName))
            r = plantSystemXml.find("./ns0:plantConstraints", self.xmlns)
            if (r is not None):
                constraintsXml = r.findall("./ns0:folders/ns0:folder/ns0:constraints//ns0:constraint", self.xmlns)
            else:
                log.warning("No plantConstraints for plant system {0}".format(plantSystemName))
            if (constraintsXml is not None):
                for constraintXml in constraintsXml:
                    constraintDescriptionXml = constraintXml.find("./ns0:description", self.xmlns)
                    constraintFunctionXml = constraintXml.find("./ns0:function", self.xmlns)
                    if (constraintFunctionXml is not None):
                        constraintFunction = constraintFunctionXml.text
                        #Remove the leading = 
                        constraintFunction = constraintFunction[1:]
                        log.debug("Loading function {0}".format(constraintFunction))
                        #Store all the variables related to this constraint function (identified by being between single quotes '')
                        variablesInConstraints = constraintFunction.split("'")[1::2]
                        #Some of the variables in the function might have been registered with a relative path (this shall be deprecated in the future)
                        allVariablesInConstraintsFullName = []
                        for variableInConstraint in variablesInConstraints:
                            #If the variable does not contain the struct separator, get the full path for the variable => variable was relative
                            if (variableInConstraint.find(self.structSeparator) == -1):
                                log.debug("Looking for the variableXmlFullPath {0}".format(variableInConstraint))
                                variableInConstraintFullName = self.getAbsoluteVariableName(xmlRoot, variableInConstraint)
                                if (variableInConstraintFullName is not None):
                                    log.debug("Found the variableXmlFullPath {0}".format(variableInConstraintFullName))
                                    #Patch the constraintsFunction to update to the full variable path
                                    constraintFunction = constraintFunction.replace(variableInConstraint, variableInConstraintFullName)
                                    allVariablesInConstraintsFullName.append(variableInConstraintFullName)
                                else:
                                    log.critical("Could not find absolute path for variable {0}".format(variableInConstraint))
                            else:
                                allVariablesInConstraintsFullName.append(variableInConstraint)
                        for variableInConstraint in allVariablesInConstraintsFullName:
                            try:
                                constraints[variableInConstraint].append(constraintFunction)
                                log.debug("Appending {0} for function {1}".format(variableInConstraint, constraintFunction))
                            except KeyError as e:
                                constraints[variableInConstraint] = [constraintFunction]
                                log.debug("Registering {0} for function {1}".format(variableInConstraint, constraintFunction))
                    else:
                        log.warning("No constraint function defined in plant system {0}".format(plantSystemName))
            else:
                log.warning("No folders/folder/constraints for plant system {0}".format(plantSystemName))

        return constraints

    def attachVariableConstraints(self, variable, parentName, globalConstraints):
        #Check if the variable is in the constraints list
        if (variable.getName() in globalConstraints):
            log.debug("Attaching {0} to variable {1}".format(globalConstraints[variable.getName()], variable.getName()))
            variable.setValidations(globalConstraints[variable.getName()])
        members = variable.getMembers()
        for memberName, memberVariable in members.iteritems():
            memberFullName = parentName + self.structSeparator + memberName
            log.debug("Looking for variable {0}".format(memberFullName))
            if (memberFullName in globalConstraints):
                memberVariable.setValidations(globalConstraints[memberFullName])
                log.debug("Attaching {0} to variable {1}".format(globalConstraints[memberFullName], memberFullName))
            self.attachVariableConstraints(memberVariable, memberFullName, globalConstraints)

    def getVariablesInfo(self, pageName, requestedVariables):
        xmlFileLocation = "{0}/psps/configuration/{1}/000/plant.xml".format(self.baseDir, pageName)
        log.debug("Loading plant configuration from {0}".format(xmlFileLocation))
        perfStartTime = timeit.default_timer()
        variables = []
        xmlId = self.getXmlId(xmlFileLocation)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(xmlFileLocation)

        if (tree is not None):
            xmlRoot = tree.getroot()
            constraints = self.loadConstraints(xmlRoot)
            for variableName in requestedVariables:
                variable = None
                r = self.findVariableInXml(xmlRoot, variableName)
                if (r.tag == self.recordTag): 
                    #If it pointing already inside a record just create the member variable (and set the name to the full path, so that it is clear that a variable may be part of a structure)
                    variable = self.createVariableFromRecord(r) 
                    if (variable is not None):
                        #Reset the parent to point at the member
                        variable.setName(variableName)
                else:
                    parentNameXml = r.find("./ns0:name", self.xmlns)
                    if (parentNameXml is not None):
                        parentName = parentNameXml.text
                    else:
                        parentName = ""
                    parentDescriptionXml = r.find("./ns0:description", self.xmlns)
                    if (parentDescriptionXml is not None):
                        parentDescription = parentDescriptionXml.text
                    else:
                        parentDescription = ""
                    #Set the name of the parent to the full path, so that it is clear that a variable may be part of a structure
                    parent = Variable(variableName, parentName, parentDescription)

                    #Skip the plantRecords (iff the length of the path is > 0 since I might need to read the name and the description before plantRecords)
                    pr = r.find("./ns0:plantRecords", self.xmlns)
                    if (pr is not None):
                        r = pr
                    #Recursively add all the variables information
                    variable = self.getVariableInfo(r, parent)
                    self.attachVariableConstraints(variable, variable.getName(), constraints)
                    
                if (variable is not None):
                    variables.append(variable)
        self.lockPool.release(xmlId)
        perfElapsedTime = timeit.default_timer() - perfStartTime
        log.debug("Took {0} s to get the information for all the {1} variables in the plant for page {2}".format(perfElapsedTime, len(requestedVariables), pageName))
        return variables 

    def getPages(self):
        return self.pages

    def getPage(self, pageName):
        page = None
        try:
            idx = self.pages.index(pageName)
        except ValueError as e:
            log.critical("Failed to get page {0}".format(e))
            idx = -1
        if (idx >= 0):
            page = self.pages[idx]
        return page

    def getLibraries(self, username, htype):
        log.debug("Getting libraries for library type: {0} for user {1}".format(htype, username))
        libraries = []
        allLibrariesXml = self.getAllLibrariesXmls(username, htype)

        for xmlFile in allLibrariesXml:
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
            name = filePath[-1]
            name = name.split(".xml")
            if (len(name) > 1):
                name = name[-2]
            library = HLibrary(htype, xmlFile, name, username, description)
            libraries.append(library);

        return libraries

    def getSchedules(self, username, pageName):
        schedules = []
        allSchedulesXml = self.getAllSchedulesXmls(username, pageName)

        for xmlFile in allSchedulesXml:
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
            name = filePath[-1]
            name = name.split(".xml")
            if (len(name) > 1):
                name = name[-2]
            schedule = Schedule(xmlFile, name, pageName, username, description)
            schedules.append(schedule);

        return schedules

    def getSchedule(self, scheduleUID):
        schedule = None
        xmlId = self.getXmlId(xmlFile)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(xmlFile)
        if (tree is not None):
            xmlRoot = tree.getroot()
            description = xmlRoot.find("./ns0:description", self.xmlns)
            if (description is not None):
                description = description.text
            filePath = xmlFile.split("/")
            schedule = Schedule(xmlFile, filePath[-1], pageName, username, description)
        self.lockPool.release(xmlId)
        return schedule

    def getScheduleVariablesValues(self, scheduleUID):
        log.debug("Return schedule variables values for UID: {0}".format(scheduleUID))
        xmlId = self.getXmlId(scheduleUID)
        self.lockPool.acquire(xmlId)
        variables = self.getAllVariablesValues(scheduleUID)
        self.lockPool.release(xmlId)
        log.debug("Returning variables: {0}".format(variables))
        return variables

    def getLibraryVariablesValues(self, libraryUID):
        log.debug("Return library variables values for UID: {0}".format(libraryUID))
        xmlId = self.getXmlId(libraryUID)
        self.lockPool.acquire(xmlId)
        variables = {}
        tree = self.getCachedXmlTree(libraryUID)
        if (tree is not None):
            xmlRoot = tree.getroot()
            structuredVariablesXml = xmlRoot.findall("./ns0:folders/ns0:folder", self.xmlns)
            for structuredVariableXml in structuredVariablesXml:
                structuredVariableName = structuredVariableXml.find("./ns0:name", self.xmlns).text
                log.debug("Getting variables values for library variable {0}".format(structuredVariableName))
                self.getVariableValue(structuredVariableXml, structuredVariableName, variables)
           
            #Append non structure variables (if any) 
            records = xmlRoot.find("./ns0:records", self.xmlns)
            if (self.containsRecords(records)):
                records = records.findall("./ns0:record", self.xmlns)
                for rec in records:
                    self.getRecord(rec, variables)
        else:
            log.critical("Could not find the xml tree for {0}".format(xmlId))
        return variables

        self.lockPool.release(xmlId)
        log.debug("Returning variables: {0}".format(variables))
        return variables

    def commitSchedule(self, tid, scheduleUID, variables):
        updatedVariables = {}
        xmlId = self.getXmlId(scheduleUID)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(scheduleUID)
        if (tree is not None):
            root = tree.getroot()
            for name in variables:
                value = variables[name]
                if(self.updateVariable(name, root, value)):
                    updatedVariables[name] = value
        tree.write(scheduleUID)
        self.lockPool.release(xmlId)
        return updatedVariables 

    def updatePlant(self, pageName, variables):
        updatedVariables = {}
        xmlPath = "{0}/psps/configuration/{1}/000/plant.xml".format(self.baseDir, pageName)
        xmlId = self.getXmlId(xmlPath)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            root = tree.getroot()
            for name in variables:
                value = variables[name]
                if(self.updateVariable(name, root, value)):
                    updatedVariables[name] = value
        tree.write(xmlPath)
        self.lockPool.release(xmlId)
        return updatedVariables 

    def createSchedule(self, name, description, username, pageName, sourceScheduleUID):
        ok = True
        log.info("Creating a new schedule for user: {0} for page: {1} with name: {2}".format(username, pageName, name))
        if (sourceScheduleUID is None):
            sourceScheduleUID = "{0}/psps/configuration/{1}/000/plant.xml".format(self.baseDir, pageName)
            destFolderNumber = "000"
        else: 
            filePath = sourceScheduleUID.split("/")
            if (len(filePath) < 2):
                log.critical("Could not parse the sourceScheduleUID {0} to find the last folder name (which should be a number)".format(sourceScheduleUID))
                ok = False
            destFolderNumber = filePath[-2]

        if (ok):
            if (not name.endswith(".xml")):
                name = name + ".xml"
            if (self.standalone):
                destScheduleDirs = "{0}/psps/configuration/{1}/{2}/".format(self.baseDir, pageName, destFolderNumber)
                destScheduleUID = "{0}/psps/configuration/{1}/{2}/{3}".format(self.baseDir, pageName, destFolderNumber, name)
            else:
                destScheduleDirs = "{0}/users/{1}/configuration/{2}/{3}/".format(self.baseDir, username, pageName, destFolderNumber)
                destScheduleUID = "{0}/users/{1}/configuration/{2}/{3}/{4}".format(self.baseDir, username, pageName, destFolderNumber, name)
            try:
                os.makedirs(destScheduleDirs)
            except OSError as e:
                if (e.errno != errno.EEXIST):
                    #Ignore the file exists error
                    log.critical("Failed to create schedule directory {0}".format(e))
            
            try:
                shutil.copy2(sourceScheduleUID, destScheduleUID) 
            except IOError as e:
                log.critical("Failed to create schedule {0}".format(e))
                ok = False

        if (ok):
            xmlId = self.getXmlId(destScheduleUID)
            self.lockPool.acquire(xmlId)
            tree = self.getCachedXmlTree(destScheduleUID)
            if (tree is not None):
                xmlRoot = tree.getroot()
                nameXml = xmlRoot.find("./ns0:name", self.xmlns)
                if (nameXml is not None):
                    nameXml.text = name 
                descriptionXml = xmlRoot.find("./ns0:description", self.xmlns)
                if (descriptionXml is not None):
                    descriptionXml.text = description
                tree.write(destScheduleUID)
                log.info("Created schedule with uid {0}".format(destScheduleUID))
            else:
                log.critical("Failed to create schedule with uid {0}".format(destScheduleUID))
            self.lockPool.release(xmlId)
        return destScheduleUID

    def convertVariableTypeFromXml(self, xmlVariableType):
        """ Helper function which converts a psps record type to a hieratika type.
        
        Args:
            xmlVariableType(str): the psps record type to convert.
        Returns:
            The hieratika converted type.
        """
        toReturn = "string"
        if (xmlVariableType == "recordLong"):
            toReturn = "int32" 
        elif (xmlVariableType == "recordFloat"):
            toReturn = "float32" 
        elif (xmlVariableType == "recordDouble"):
            toReturn = "float64" 
        elif (xmlVariableType == "recordString"):
            toReturn = "string" 
        elif (xmlVariableType == "recordEnum"):
            toReturn = "enum" 
        elif (xmlVariableType == "recordLibrary"):
            toReturn = "library" 
        else:
            log.critical("Could not convert type {0}".format(xmlVariableType))
        return toReturn

    def getAllLibrariesXmls(self, username, htype):
        """ Helper function which gets all libraies associated to a given page for a given library type.
       
        Args:
            username (str): the username to search.
            htype (str): the library type  to search.
        Returns:
            All the libraries files found for a given type.
        """
        matches = []
        if (self.standalone):
            directory = "{0}/psps/libraries/{1}".format(self.baseDir, htype)
        else:
            directory = "{0}/users/{1}/libraries/{2}".format(self.baseDir, username, htype)
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.xml'):
                matches.append(os.path.join(root, filename))
        return matches


    def getAllSchedulesXmls(self, username, pageName):
        """ Helper function which gets all psps configurations associated to a given page for a given user.
       
        Args:
            username (str): the username to search.
            pageName (str): the configuration to search.
        Returns:
            All the schedules files found for a given configuration.
        """
        matches = []
        if (self.standalone):
            directory = "{0}/psps/configuration/{1}".format(self.baseDir, pageName)
        else:
            directory = "{0}/users/{1}/configuration/{2}".format(self.baseDir, username, pageName)
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.xml'):
                if (filename != "plant.xml"):
                    matches.append(os.path.join(root, filename))
        return matches

    def loadPages(self):
        """ Loads the list of available pages (which corresponds to the number of different configurations).
            Note that the plant.xml file is automatically created if needed (i.e. if it doesn't exist).
        """
        if (self.baseDir == "~"):
            self.baseDir = os.path.expanduser("~")
        directory = "{0}/psps/configuration/".format(self.baseDir)
        log.info("Loading pages from folder {0}".format(directory))
        for root, dirnames, filenames in os.walk(directory):
            for dirname in dirnames:
                page = Page(dirname, dirname, dirname)
                self.pages.append(page)
                log.info("Registered page {0}".format(page))
                plantXmlFound = False
                latestXmlFound = None
                #Check if there is a plant.xml. If not create one based on the latest .xml that was found
                for rootPlantXml, dirnamesPlantXml, filenamesPlantXml in os.walk(root + "/" + dirname):
                    for f in filenamesPlantXml:
                        if (f.endswith(".xml")):
                            latestXmlFound = rootPlantXml + "/" + f
                        plantXmlFound = (f == "plant.xml")
                        if (plantXmlFound):
                            break
                    if (plantXmlFound):
                        break
                plantXmlFileLocation = "{0}/{1}/000/plant.xml".format(directory, page.name)
                if (plantXmlFound):
                    log.info("Found the plant.xml for configuration {0}".format(page.name))
                else:
                    log.warning("Could not find the plant.xml for configuration {0}".format(page.name))
                    if (latestXmlFound is not None):
                        log.warning("For {0}, going to create the plant.xml based on {1}".format(page.name, latestXmlFound))
                        try:
                            shutil.copy2(latestXmlFound, plantXmlFileLocation) 
                        except IOError as e:
                            log.critical("Failed to create the plant.xml {0}".format(e))
                    else:
                        log.warning("No configuration xml was found for {0}".format(page.name))

                #Check if the page html exists
                pageHtmlPath = "{0}/{1}.html".format(self.pagesFolder, page.name)
                if (not os.path.exists(pageHtmlPath)):                
                    log.warning("The {0} file does not exist".format(pageHtmlPath))
                    if (self.autoCreatePages):
                        self.createHtmlPage(pageHtmlPath, plantXmlFileLocation)
                
                    
            #Only want the first sub level
            break

    def createHtmlPage(self, htmlPagePath, plantXmlPath):
        """ Creates a basic html page to display the plant. This is likely to be deprecated in the future since it couples the server
            with an assumption that the client is the html viewer.
        """
        html = """ <html>
                    <head>
                     <link rel='import' href='/pmc-struct-browser.html'>
                    </head>
                    <body>
               """
        tree = self.getCachedXmlTree(plantXmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            plantSystemsRootXml = xmlRoot.findall(".//ns0:plantSystem", self.xmlns)
            for plantSystemXml in plantSystemsRootXml:
                plantSystemName = plantSystemXml.find("./ns0:name", self.xmlns).text
                html += "<pmc-struct-browser id='{0}' name='{0}'></pmc-struct-browser>".format(plantSystemName)

            html += """ </body>
                       </html>
                    """

            try:
                with open (htmlPagePath, "w") as f:
                    f.write(html)
                    log.info("Created the hmtl page for {0}".format(htmlPagePath))
            except Exception as e:
                log.critical("Could not create the hmtl page for {0}".format(htmlPagePath))
        else:
            log.critical("Could not load {0}".format(plantXmlPath))

    def getCachedXmlTree(self, xmlPath):
        """ Parses the xml defined by the xmlPath and caches it in memory.
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            
            Args:
                xmlPath (str): path to the xml file to be parsed.
            Returns:
                The parsed Xml file or None if an error occurs.
        """
        self.mux.acquire()
        if (len(self.cachedXmls) > self.maxXmlCachedTrees):
            log.info("Reached maximum number of cached xml trees :{0} > {1}".format(len(self.cachedXmls), self.maxXmlCachedTrees))
            toDeleteMaxSize = (len(self.cachedXmls) / 2) + 1
            #Sort by access time. Remember that the values of cachedXmls are tupples containing the path, the parsed Element and the last access time
            sortedByTime = sorted(self.cachedXmls.values(), key=lambda tup:tup[2])
            i = 0
            while i < toDeleteMaxSize:
                log.debug("Deleting xml (from memory) with key {0}".format(sortedByTime[i][0]))
                del(self.cachedXmls[sortedByTime[i][0]])
                i = i + 1
            log.info("After cleaning the number of cached xml is {0}".format(len(self.cachedXmls)))


        try:
            ret = self.cachedXmls[xmlPath][1]
            self.cachedXmls[xmlPath][2] = time.time()
        except Exception as e:
            try:
                #The xmlPath is also stored as value in order to accelerate the cleaning above
                self.cachedXmls[xmlPath] = (xmlPath, etree.parse(xmlPath), time.time())
                ret = self.cachedXmls[xmlPath][1]
            except Exception as e:
                log.critical("Error loading xml file {0}: {1}".format(xmlPath, str(e)))
                ret = None
        self.mux.release()
        return ret

    def updateVariable(self, variableName, root, variableValue):
        """ Updates the value of the a variable in a given xml (plant or schedule).
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            Note that this change is not sinked to disk.
    
        Args:
            variableName (str): the name of the variable to update.
            root (Element node): the root of the xml to be updated.
            variableValue (str): the value of the variable to be updated.

        Returns:
            True if the variable is sucessfully updated.
        """

        #Allow only one process to interact with a given xml at the time
        #Makes sure that this is both multi-processing and multi-threading safe
        log.debug("Updating {0} with value {1}".format(variableName, variableValue))

        ok = False
        #TODO for the time being I will encode the plant system name as the first structSeparator token. This needs discussion at some stage
        idx = variableName.find(self.structSeparator)
        if (idx != -1):
            plantSystemName = variableName[:idx]
            variableName = variableName[idx + 1:]
            path = variableName.split(self.structSeparator)
           
            r = root.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']/ns0:plantRecords".format(plantSystemName), self.xmlns)
            fullVariablePath = "." 
            for p in path[:-1]:
                fullVariablePath = fullVariablePath + "/ns0:folders/ns0:folder[ns0:name='{0}']".format(p)

            fullVariablePath = fullVariablePath + "/ns0:records/ns0:record[ns0:name='{0}']".format(path[-1])
            recordXml = r.find(fullVariablePath, self.xmlns)
            if (recordXml is not None):
                valuesXml = recordXml.find("./ns0:values", self.xmlns)
                if (valuesXml is not None):
                    recordXml.remove(valuesXml)
                valuesXml = etree.SubElement(recordXml, "{{{0}}}values".format(self.xmlns["ns0"]))
                valueXml = etree.SubElement(valuesXml, "{{{0}}}value".format(self.xmlns["ns0"]))
                valueXml.text = json.dumps(variableValue)
                ok = True
            else:
                log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, fullVariablePath))
        else:
            log.critical("No plant system defined for variable {0}".format(variableName))

        return ok

    def getVariableValue(self, r, variableName, variables):
        """ Recursively gets all the variable values for a given plantSystem node in the xml.
            
            Args:
                r (xmlElement): walks the xml Tree. The first time this function is called it shall point at the plantRecords.
                variableName (str): the name of the variable. It is constructed as the function recursively walks the tree. The separator is the structSeparator symbol.
                variables (__dict__): dictionary where the value of the variable is stored.
        """
        records = r.find("./ns0:records", self.xmlns)
        if (not self.containsRecords(records)):
            r = r.find("./ns0:folders", self.xmlns)
            if (r is None):
                log.critical("Wrong xml structure. ns0:folders is missing")
                return None
            else:
                folders = r.findall("./ns0:folder", self.xmlns)
                variableNameBeforeFolders = variableName
                for f in folders:
                    n = f.find("./ns0:name", self.xmlns)
                    if (n is not None):
                        variableName = variableNameBeforeFolders + self.structSeparator + n.text
                        self.getVariableValue(f, variableName, variables)
                    else:
                        log.critical("Wrong xml structure. ns0:name is missing in folder")
        else:
            records = records.findall("./ns0:record", self.xmlns)
            variableNameBeforeRecord = variableName
            for rec in records:
                self.getRecord(rec, variables, variableNameBeforeRecord)

    def getAllVariablesValues(self, xmlPath):
        variables = {}
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            plantSystemsRootXml = xmlRoot.findall(".//ns0:plantSystem", self.xmlns)
            for plantSystemXml in plantSystemsRootXml:
                plantSystemName = plantSystemXml.find("./ns0:name", self.xmlns).text
                plantRecordsXml = plantSystemXml.find("./ns0:plantRecords", self.xmlns)
                log.debug("Getting variables values for plant system name {0}".format(plantSystemName))
                self.getVariableValue(plantRecordsXml, plantSystemName, variables)
        else:
            log.critical("Could not find the xml tree for {0}".format(xmlPath))
        return variables


    def containsRecords(self, records):
        """ 
        Returns:
            True if the xml node r is a non-empty node of type records.
        """
        hasRecords = (records is not None)
        if (hasRecords):
            hasRecords = (len(records) > 0)
        return hasRecords

    def getRecord(self, rec, variables, prefix = None):
        """ Helper function to load the value from a record.
        Args:
            rec (xml Element): the record to be queried.
            variables ({}): dictionary where to set the record name: record value
            prefix (str): to be append to the record name before updating the variables list.
        """
        n = rec.find("./ns0:name", self.xmlns)
        if (n is not None):
            variableName = n.text
            if (prefix is not None):
                variableName = prefix + self.structSeparator + variableName
            
            valuesXml = rec.find("./ns0:values", self.xmlns)
            if (valuesXml is not None):
                value = []
                #len(allValuesXml) > 1 should only happen the first time a plant/schedule is read (since the current version of the psps editor stores arrays as lists of <value></value>. In the future these lists should be deprecated. I always serialize the values in a single <value>[]</value> element when I update the plant/schedule.
                allValuesXml = valuesXml.findall("./ns0:value", self.xmlns)
                for valueXml in allValuesXml:
                    try:
                        #In order to be able to trap the case where there are strings
                        val = json.loads(valueXml.text)
                    except Exception as e:
                        val = valueXml.text
                        log.critical("Failed to load json {0}. Returning the original text.".format(e))
                    if (isinstance(val, list)):
                        if (len(value) == 0):
                            value = val
                        else:
                            value.append(val)
                    else:
                        value.append(val)
                variables[variableName] = value
            else:
                log.critical("./ns0:values is missing for variable with name {0}".format(variableName))
        else:
            log.critical("Wrong xml structure. ns0:name is missing in record")
        log.debug("Retrieved value for variable [{0}]".format(variableName))
 
