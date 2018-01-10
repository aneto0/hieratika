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
import time

##
# Project imports
##

##
# Logger configuration
##

##
# Class definition
##
class HLibrary(object):
    """ Describes a hieratika parameter library.
        An HLibrary is a collection of values that can be assigned to different variables. 
        A typical example is a waveform definition.
        The same waveform definition (i.e. the actual values) might be used by many parameters. As a consequence these parameters need only to link
        to this waveform definition (by name) in order to be configured (as opposed to be individually configured with the same values).
        Note that this is not the place where to define structured types. The same structured type might be used by many libraries. As an example, 
        a waveform structured type might be used by a library for selecting power supply references and by a library for selecting data acquisition time windows.
        This means that when linking variables from the power supply, only the waveforms which are associated to the power supply references are going to be avaiable for 
        user selection (even if any other waveforms would be type compatible). The main reasoning is that expert users will pre-cook waveforms whose content/value is meaningful
        for the given use-case (power supply references in this example).

        A library which is locked cannot be modified nor deleted from the system. This is to avoid that a given library definition is used in a given configuration and is later overriden.
    """

    def __init__(self, htype, uid, name, owner, description = "", obsolete = False):
        """ Constructs an HLibrary object against a uid, name, owner and description.
        
        Args:
            htype (str): the type of library (e.g. waveform-power-supply-A) (the same library type may have different instances, each with its uid).
            uid (str): a unique system identifier for the library.
            name (str): the name of the library.
            owner (str): the username of the User which owns the library.
            description (str): a description of the library.
            obsolete (bool): True if the schedule has been marked as obsolete.
        """
        self.htype = htype
        self.uid = uid
        self.name = name
        self.owner = owner 
        self.description = description
        self.locked = False
        self.lastModified = 0
        self.obsolete = obsolete

    def getUID(self):
        """ 
        Returns: 
            A unique system identifier for the library.
        """
        return self.uid

    def getName(self):
        """ 
        Returns:
            The library name (may not be unique).
        """
        return self.name

    def getDescription(self):
        """ 
        Returns:
            The library description.
        """
        return self.description

    def getOwner(self):
        """ 
        Returns:
            The username of the User which owns the library.
        """
        return self.owner

    def getHType(self):
        """ 
        Returns:
            The type of library (see the class description).
        """
        return self.htype

    def isLocked(self):
        """
        Returns:
            True if the library is locked and thus cannot be removed from the system.
        """
        return self.locked

    def lastModified(self):
        """
        Returns:
            The last time (in ns from the epoch) that the library was modified.
        """
        return self.lastModified

    def setLocked(self, locked):
        """
        Args (locked):
            Sets the library locked state.
        """
        self.locked = locked

    def setLastModified(self, lastModified):
        """
        Args (locked):
            Sets the last time at which the library was modified.
        """
        self.lastModified = lastModified

    def isObsolete(self):
        """ 
        Returns:
            Returns true if the library has been marked as obsolete.
        """
        return self.obsolete

    def __eq__(self, another):
        """ Two libraries are equal if they have the same uid.
           
        Args:
            self (HLibrary): this library instance.
            another (HLibrary or str): another HLibrary or a string. 
        Returns:
            True if self and another uid are equal or if another is a string whose value is the self.getUID().
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getUID() == another.getUID())
        else:
            areEqual = (self.getUID() == str(another))
        return areEqual

    def __cmp__(self, another):
        """ See __eq__
        """
        return (self == another) 

    def __hash__(self):
        """ The class is univocally identified by the uid.

        Returns:
            The uid.
        """
        return getUID()

    def __str__(self):
        """ Returns a string representation of an HLibrary.
            
        Returns:
            A string representation of an HLibrary which consists of the uid followed by the htype, name,
        description and owner username.
        """
        return "{0} {1} {2} {4} (owner:{4}, last modified: {5}, locked: {6})".format(self.uid, self.htype, self.name, self.description, self.owner, self.lastModified, self.locked) 

