#!/usr/bin/python
from socket import *
import os
import threading

class BroacastQueue:
    
    def __init__(self, port, timeout=10, hostServer="127.255.255.0", hostPublish="127.255.255.255"):
        self.port = port
        self.timeout = timeout
        self.hostServer = hostServer
        self.hostPublish = hostPublish
        self.sockets = {}

    def __del__(self):
        for k, s in self.sockets.iteritems():
            s.close()
        
    def getSocket(self, server):
        uid = str(os.getpid()) + "_" + str(threading.current_thread().ident)
        if (server):
            uid = uid + "_s"

        if (uid not in self.sockets):
            print uid
            s = socket(AF_INET, SOCK_DGRAM)
            s.settimeout(self.timeout)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            if (server):
                print "Going to listen on " + self.hostServer + ":" +  str(self.port)
                s.bind((self.hostServer, self.port))
            self.sockets[uid] = s
        return self.sockets[uid]

    def put(self, item):
        s = self.getSocket(False)
        print "Going to publish on " + self.hostPublish + ":" + str(self.port)
        s.sendto(item, (self.hostPublish, self.port))
            
    def get(self, itemSize=1024):
        s = self.getSocket(True)
        try:
            print "Waiting..."
            item = s.recvfrom(itemSize)
            print item
        except timeout:
            print "Timeout..."
            item = None 
        return item

