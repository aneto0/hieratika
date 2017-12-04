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
__date__ = "07/11/2017"


##
# Standard imports
##
import logging
import os
from socket import *
import struct
import threading

##
# Project imports
##

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class BroacastQueue:
    """ A one to many queue which allows to share objects between one and many processes.
        The implementation is based on multicast UDP sockets with a ttl of 1 (i.e. blocked to the current network segment).
    """
    
    def __init__(self, group, port, itemSize=8192, timeout=10):
        """ Constructor.
        Args:
            group (str): the multicast group to be used.
            port (int): the multicast port.
            timeout (int): maximum timeout to wait for an item to arrive. If no item arrives in this time the queue will return None.
        """
        self.group = group
        self.port = port
        self.timeout = timeout
        self.itemSize = itemSize
        self.sockets = {}

    def __del__(self):
        """ Destructor.
            Closes all the queue sockets.
        """
        for k,  sock in self.sockets.iteritems():
             sock.close()
        
    def getSocket(self, receiver):
        """ Gets a socket. A socket will be cached for every pid/tid pair.
    
        Args:
            receiver (boolean): True if the socket is a receiver.
        Returns:
            An UDP multicast socket.
        """
        uid = str(os.getpid()) + "_" + str(threading.current_thread().ident)
        if (receiver):
            uid = uid + "_rec"
        if (uid not in self.sockets):
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sock.settimeout(self.timeout)
            if (receiver):
                mgroup = inet_aton(self.group)
                mreq = struct.pack('4sL', mgroup, INADDR_ANY)
                sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
                sock.bind((self.group, self.port))
            else:
                # Set the time-to-live for messages to 1 so they do not go past the local network segment.
                ttl = struct.pack('b', 1)
                sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
            self.sockets[uid] = sock 
        return self.sockets[uid]

    def put(self, item):
        """ Puts an item in the queue and warns all the registered receivers.
        
        Args:
            item (str): the item to be sent.
        """
        sock = self.getSocket(False)
        sock.sendto(item, (self.group, self.port))
            
    def get(self):
        """ Gets an item from queue.
        
        Args:
            itemSize (int): maximum item size to be received.
        Returns:
            The received item or None if a timeout occurs.
        """

        sock = self.getSocket(True)
        try:
            item, address = sock.recvfrom(self.itemSize)
        except timeout:
            item = None 
        return item

