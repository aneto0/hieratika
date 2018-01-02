#!/usr/bin/env python

""" A multiprocessing, multithreading, pool of named semaphores.
"""
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
import logging
import multiprocessing
import multiprocessing.managers
import os
import time
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
class LockPool(object):
    """ A multiprocessing, multithreading, pool of named semaphores.

        Semaphores are identified by a key at the time of acquire and release.
        A semaphore associated to a given key will guarantee both multiprocessing and multithreading locking.
        It should be noted that the same process is allowed to acquire different named semaphores (using multithreading).

        The first time a key is acquired a multiprocessing.Lock is retrieved from a pool of semaphores. Subsequent acquires
        will either lock the process (if it is first time the caller process is acquiring this key) or the thread
        (after the second time the same caller process is acquiring the same key).

        When a key is released, if no more threads or processes are waiting on that key, the semaphore is returned to the pool.

    Args:
        numberOfLocks (int): the maximum number of simultaneous locks (i.e. different keys) that is allowed to lock on this pool.
    """

    def __init__(self, numberOfLocks):
        #MUST use a different manager instance for every group (where a group is a set of dictionaries which are
        #guaranteed to have exclusive access (read and read/write) to its elements. See https://stackoverflow.com/questions/48052148/python-multiprocessing-dict-sharing-between-processes ).
        self.manager = multiprocessing.managers.SyncManager()
        self.manager.start()
        #Global mux to protect access to shared counter (I have tested that this also protects against multi-threading in the scope of the same process)
        self.mux = self.manager.Lock()
        #Counts the number of locks that were allocated to a given key. Note that this has to be done this way as no multiprocessing semaphores nor multiprocessing dicts can be created after the child processes are forked (given that these will have a local copy of all the variables)
        self.allocatedLocksC = self.manager.dict()
        #Stores the self.sharedLocks array index that is assigned to a given key
        self.allocatedLocksI = self.manager.dict()
        #The pool of semaphores. One different semaphore will be allocated for each key
        self.sharedLocks = []
        #Stores the indexes of the semaphores which are ready to be used
        self.sharedLocksFreeState = self.manager.list()
        for i in range(numberOfLocks):
            self.sharedLocks.append(multiprocessing.Lock())
            self.sharedLocksFreeState.append(True)

    def acquire(self, key):
        """ Acquires a lock against a given key.
        
            Args:
                key (str): a unique identifier for the semaphore to be locked.
        """
        self.mux.acquire()
        pid = str(os.getpid())
        log.critical("A0 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        #print self.allocatedLocksC
        #Check if there is already a key with this lock
        if (key in self.allocatedLocksC):
            #Since this key was already locked, it can have been locked by another process or by this same process using
            #another thread
            log.critical("A0.1 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            self.allocatedLocksC[key] = self.allocatedLocksC[key] + 1
            log.critical("A1 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            idx = self.allocatedLocksI[key]
            log.debug("The process with pid: {0} had already locked the key (with another thread): {1}. Thread: {2}. Number of locks for this key:{3} idx:{4} L:{5} @ {6}".format(pid, key, threading.current_thread().ident, self.allocatedLocksC[key], id(idx), self.sharedLocks[idx], id(self.sharedLocks[idx])))
            lock = self.sharedLocks[idx]
            log.critical("A2 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            self.mux.release()
            lock.acquire()
            log.critical("A3 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        else:
            #Get a free lock
            try:
                log.critical("A0.2 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                #No one has ever requested to lock on this key, so just lock the process and prepare a shared lock
                idx = int(self.sharedLocksFreeState.index(True))
                #Get a multiprocessing semaphore which in not being used now. If this fails the exception below will be raised
                log.critical("A4 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                self.allocatedLocksC[key] = 1
                log.critical("A5 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                self.allocatedLocksI[key] = idx
                log.critical("A6 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                self.sharedLocksFreeState[idx] = False
                log.critical("A7 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                #Lock on the process
                log.debug("The process with pid: {0} is the first to lock key: {1}. Thread: {2} {3} L:{4} @ {5}".format(pid, key, threading.current_thread().ident, id(idx), self.sharedLocks[idx], id(self.sharedLocks[idx])))
                #Note that this will block the calling thread from this process but not other threads from the same process
                self.sharedLocks[idx].acquire()
                log.critical("A8 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
                self.mux.release()
            except ValueError:
                #No locks available on the shared pool. Poll for resources to be available...
                self.mux.release()
                warned = False
                while(True not in self.sharedLocksFreeState):
                    if (not warned):
                        log.critical("No locks available on the shared pool. Sleeping while waiting for available resources.")
                        warned = True
                    time.sleep(1e-2)
                return self.acquire(key)

    def release(self, key):
        """ Releases a lock that was acquired against a given key.
        
            Args:
                key (str): the unique identifier that was used to lock the semaphore.
        """
        self.mux.acquire()
        pid = str(os.getpid())
        log.critical("R0 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        idx = int(self.allocatedLocksI[key])
        log.critical("R1 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        log.debug("Releasing process with pid: {0} for key: {1}. Thread: {2} {3} L:{4} @ {5}".format(pid, key, threading.current_thread().ident, id(idx), self.sharedLocks[idx], id(self.sharedLocks[idx]))) 
        lock = self.sharedLocks[idx]
        log.critical("R2 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        self.allocatedLocksC[key] = self.allocatedLocksC[key] - 1
        if (self.allocatedLocksC[key] == 0):
            log.debug("The process with pid: {0} was the last locking the key: {1} so that the semaphore will be returned to the pool. Thread: {2}".format(pid, key, threading.current_thread().ident)) 
            log.critical("R3 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            # If there are no more processes interested give it back to the pool 
            self.sharedLocksFreeState[idx] = True 
            log.critical("R3.1 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            self.allocatedLocksC.pop(key) 
            log.critical("R3.2 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
            self.allocatedLocksI.pop(key)
            log.critical("R4 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        else: 
            log.debug("The process with pid: {0} is releasing the key: {1}. Thread: {2}. Number of locks: {3}".format(pid, key, threading.current_thread().ident, self.allocatedLocksC[key]))
            log.critical("R5 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        log.critical("R6 {0} {1}>>>> {2} {3} {4}".format(key, pid, self.allocatedLocksC, self.allocatedLocksI, self.sharedLocksFreeState))
        lock.release()
        self.mux.release()
               
    def isKeyInUse(self, key): 
        """ Checks if a given key is currently being used.
        Returns:
            True if the key currently being used to lock a semaphore in the pool.
        """
        self.mux.acquire()
        ret = (key in self.allocatedLocksC)
        self.mux.release()
        return ret

