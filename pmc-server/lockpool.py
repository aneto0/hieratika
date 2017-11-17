import logging
import multiprocessing
import os
import time
import threading
log = logging.getLogger("psps-{0}".format(__name__))

class LockPool:
    """ 
    """

    def __init__(self, numberOfProcessLocks):
        self.mux = multiprocessing.RLock()
        self.manager = multiprocessing.Manager()
        self.allocatedLocksC = self.manager.dict()
        self.allocatedLocksI = self.manager.dict()
        self.sharedLocks = []
        self.sharedLocksFreeState = self.manager.list()
        i = 0
        while (i < numberOfProcessLocks):
            self.sharedLocks.append(multiprocessing.Lock())
            self.sharedLocksFreeState.append(True)
            i = i + 1

        #Note that after forking this will be one per child process, so that there will be a unique copy
        # of this dictionary for every forked child (which will have its own list of processes)
        self.processThreads = {}
        

    def acquire(self, key):
        self.mux.acquire()
        pid = str(os.getpid())
        if (key not in self.processThreads):
            self.processThreads[key] = {}
            self.processThreads[key]["tcounter"] = 0
            self.processThreads[key]["tlock"] = threading.Lock()
        #Check if there is already a key with this lock
        if (key in self.allocatedLocksC):
            #Check if there is already a tid for this pid (if this same pid already tried to lock once in the context of another thread)
            if (self.processThreads[key]["tcounter"] > 0):
                print "REUSING PROCESS {0}-{1} {2}".format(pid, threading.current_thread().ident, key)
                #Lock on the thread of the pid
                self.processThreads[key]["tcounter"] = self.processThreads[key]["tcounter"] + 1
                self.mux.release()
                #Lock on the thread of the other pid
                self.processThreads[key]["tlock"].acquire()
            else:
                #Create a thread which allows subsequent calls with the same pid to lock on the thread context
                self.processThreads[key]["tcounter"] = 1
                self.processThreads[key]["tlock"].acquire()
                self.allocatedLocksC[key] = self.allocatedLocksC[key] + 1
                idx = self.allocatedLocksI[key]
                #Lock on the process
                print "NEW PROCESS FOR EXISTING KEY {0}-{1} {2}".format(pid, threading.current_thread().ident, key)
                self.mux.release()
                self.sharedLocks[idx].acquire()
        else:
            #Get a free lock
            try:
                idx = self.sharedLocksFreeState.index(True)
                #Get a semaphore which in not being used now
                self.allocatedLocksC[key] = 1
                self.allocatedLocksI[key] = idx
                self.sharedLocksFreeState[idx] = False

                #Create a thread which allows subsequent calls with the same pid to lock on the thread context
                self.processThreads[key]["tcounter"] = 1
                self.processThreads[key]["tlock"].acquire()
                #Lock on the process
                self.sharedLocks[idx].acquire()
                print "NEW PROCESS FOR NEW KEY {0}-{1} {2}".format(pid, threading.current_thread().ident, key)
                self.mux.release()
            except ValueError:
                #No locks available on the shared pool
                #Poll for resources to be available...
                self.mux.release()
                warned = False
                while(True not in self.sharedLocksFreeState):
                    if (not warned):
                        log.critical("No locks available on the shared pool. Sleeping to wait for available resources.")
                        warned = True
                    time.sleep(1e-2)
                return self.acquire(key)

    def release(self, key):
        self.mux.acquire()
        pid = str(os.getpid())
        #Check if this pid was locked on a thread semaphore (i.e. several threads were concurring from the same pid)
        self.processThreads[key]["tcounter"] = self.processThreads[key]["tcounter"] - 1
        #Release the thread
        self.processThreads[key]["tlock"].release()
        if (self.processThreads[key]["tcounter"] == 0):
            self.allocatedLocksC[key] = self.allocatedLocksC[key] - 1
            #Release the process lock
            idx = self.allocatedLocksI[key]
            print "RELEASING PROCESS AS NO MORE THREADS EXIST FOR PROCESS {0}-{1} {2}".format(pid, threading.current_thread().ident, key)
            self.sharedLocks[idx].release()
        else:
            print "RELEASING THREAD BUT OTHER THREADS STILL EXIST FOR PROCESS {0}-{1} {2}".format(pid, threading.current_thread().ident, key)

        if (self.allocatedLocksC[key] == 0):
            print "SEMAPHORE NO LONGER NEEDED!! {0}-{1} {2}".format(pid, threading.current_thread().ident, key)
            # If there are no more processes interested give back the global semaphore
            self.sharedLocksFreeState[idx] = True
            self.allocatedLocksC.pop(key)
            self.allocatedLocksI.pop(key)
            self.processThreads.pop(key)
        self.mux.release()
                
