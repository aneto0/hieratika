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
    """

    def __init__(self, numberOfProcessLocks):
        #Global mux to protect access to shared counter
        self.mux = multiprocessing.RLock()
        self.manager = multiprocessing.Manager()
        #Counts the number of locks that were allocated to a given key. Note that this has to be done this way as no multiprocessing semaphores nor multiprocessing dicts can be created after the child processes are forked (given that these will have a local copy of all the variables)
        self.allocatedLocksC = self.manager.dict()
        #Stores the self.sharedLocks array index that is assigned to a given key
        self.allocatedLocksI = self.manager.dict()
        #The pool of semaphores. One different semaphore will be allocated for each key
        self.sharedLocks = []
        #Stores True in all the indexes that are not being used by any key
        self.sharedLocksFreeState = self.manager.list()
        for i in range(numberOfProcessLocks):
            self.sharedLocks.append(multiprocessing.Lock())
            self.sharedLocksFreeState.append(True)

        #Note that after forking there will be one independent copy of processThreads per child process, so that there will be a unique copy
        # of this dictionary for every forked child (which will have its own list of threads)
        self.processThreads = {}

    def acquire(self, key):
        """ Acquires a lock against a given key.
        
            Args:
                key (str): a unique identifier for the semaphore to be locked.
        """
        self.mux.acquire()
        pid = str(os.getpid())
        #Register threads for this key in this pid. Remember that self.processThreads is local to the child process
        if (key not in self.processThreads):
            self.processThreads[key] = {}
            self.processThreads[key]["tcounter"] = 0
            self.processThreads[key]["tlock"] = threading.Lock()
        #Check if there is already a key with this lock
        if (key in self.allocatedLocksC):
            #Since this key was already locked, it can have been locked by another process or by this same process using
            #another thread
            if (self.processThreads[key]["tcounter"] > 0):
                #Case where this pid had already requested a lock for this key
                log.debug("The process with pid: {0} had already requested to lock key: {1}. Going to lock on the thread. Thread: {2}.".format(pid, key, threading.current_thread().ident))
                #Increment the number of locks associated to the same pid (remember processThreads is local to the child and thus the pid)
                self.processThreads[key]["tcounter"] = self.processThreads[key]["tcounter"] + 1
                self.mux.release()
                #Lock on the thread
                self.processThreads[key]["tlock"].acquire()
            else:
                #Case where this pid is asking for the first time for a lock for this key
                #Create a thread which allows subsequent calls with the same pid to lock on the thread context
                log.debug("The process with pid: {0} is requesting for the first time to lock key: {1} (which had already been locked by another process). Thread: {2}.".format(pid, key, threading.current_thread().ident))
                self.processThreads[key]["tcounter"] = 1
                self.processThreads[key]["tlock"].acquire()
                #Increment the number of processes that are locked on this key
                self.allocatedLocksC[key] = self.allocatedLocksC[key] + 1
                idx = self.allocatedLocksI[key]
                #Lock on the process
                self.mux.release()
                self.sharedLocks[idx].acquire()
        else:
            #Get a free lock
            try:
                #No one has ever requested to lock on this key, so just lock the process and prepare a thread lock
                # in case another thread from this pid requests a lock for the same key
                idx = self.sharedLocksFreeState.index(True)
                #Get a multiprocessing semaphore which in not being used now. If this fails the exception below will be raised
                self.allocatedLocksC[key] = 1
                self.allocatedLocksI[key] = idx
                self.sharedLocksFreeState[idx] = False
                self.processThreads[key]["tcounter"] = 1
                self.processThreads[key]["tlock"].acquire()
                #Lock on the process
                log.debug("The process with pid: {0} is the first to lock key: {1}. Thread: {2}.".format(pid, key, threading.current_thread().ident))
                #Note that this will block the calling thread from this process but not other threads from the same process
                self.sharedLocks[idx].acquire()
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
        self.processThreads[key]["tcounter"] = self.processThreads[key]["tcounter"] - 1
        #Release the thread locking this key. Note that a thread is always acquired at lock creation
        self.processThreads[key]["tlock"].release()
        if (self.processThreads[key]["tcounter"] == 0):
            #If no more threads for this pid (remember processThreads is local to the pid), release the process lock
            self.allocatedLocksC[key] = self.allocatedLocksC[key] - 1
            #Release the process lock
            idx = self.allocatedLocksI[key]
            log.debug("The process with pid: {0} has no more threads locking the key: {1} and will be released. Thread: {2}.".format(pid, key, threading.current_thread().ident))
            self.sharedLocks[idx].release()
        else:
            log.debug("The process with pid: {0} still has more threads locking the key: {1} so that only the thread will be released. Thread: {2}.".format(pid, key, threading.current_thread().ident))

        if (self.allocatedLocksC[key] == 0):
            log.debug("The process with pid: {0} was the last locking the key: {1} so that the semaphore will be returned to the pool. Thread: {2}.".format(pid, key, threading.current_thread().ident))
            # If there are no more processes interested give it back to the pool
            self.sharedLocksFreeState[idx] = True
            self.allocatedLocksC.pop(key)
            self.allocatedLocksI.pop(key)
            self.processThreads.pop(key)
        self.mux.release()
                
