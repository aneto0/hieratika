#!/usr/bin/python
from socket import *
import os
import struct
import threading

class BroacastQueue:
    
    def __init__(self, port, timeout=10, group="239.0.79.55"):
        self.port = port
        self.timeout = timeout
        self.group = group
        self.sockets = {}

    def __del__(self):
        for k,  sock in self.sockets.iteritems():
             sock.close()
        
    def getSocket(self, receiver):
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
        sock = self.getSocket(False)
        sock.sendto(item, (self.group, self.port))
            
    def get(self, itemSize=1024):
        sock = self.getSocket(True)
        try:
            item, address =  sock.recvfrom(itemSize)
        except timeout:
            item = None 
        return item

