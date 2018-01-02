import multiprocessing
import threading
import time
import os

class A:
    def __init__(self, m, mux):
        self.mux = mux
        #Each instance will have its own (independent) dictionary instance and mux
        if (m == None):
            m = multiprocessing.managers.SyncManager()
            m.start()
        self.d = m.dict()
        self.key = id(self)

    def run(self):
        self.mux.acquire()
        if (self.d.has_key(self.key)):
            item = self.d.get(self.key)
            self.d.update([(self.key, item + 1)])
            #print "{0} {1} {2}".format(os.getpid(), threading.current_thread().ident, self.d)
        else:
            self.d[self.key] = 0
        self.mux.release()
        
def run(inst, nRuns):
    for i in range(nRuns):
        inst.run()

def runThreaded(inst1, inst2, nRuns, nThreads):
    threads = []
    for i in range(nThreads):
        threads.append(threading.Thread(target=run, args=(inst1, nRuns)))
        threads.append(threading.Thread(target=run, args=(inst2, nRuns)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def test_sameProcessSameThread(inst1, inst2, nRuns):
    print "Starting test_sameProcessSameThread"
    run(inst1, nRuns) 
    run(inst2, nRuns) 
    print "Finished test_sameProcessSameThread"

def test_sameProcessThreaded(inst1, inst2, nRuns, nThreads):
    print "Starting test_sameProcessThreaded"
    runThreaded(inst1, inst2, nRuns, nThreads) 
    print "Finished test_sameProcessThreaded"

def test_manyProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses):
    print "Starting test_manyProcessesSingleThreaded"

    procs = []
    for i in range(nProcesses):
        procs.append(multiprocessing.Process(target=run, args=(inst1, nRuns)))
        procs.append(multiprocessing.Process(target=run, args=(inst2, nRuns)))

    for p in procs:
        p.start()

    for p in procs:
        p.join()

    print "Finished test_manyProcessesSingleThreaded"


def test_manyForkedProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses):
    print "Starting test_manyForkedProcessesSingleThreaded"
    forkedPids = []
    for i in range(nProcesses):
        newpid = os.fork()                                                                                                                  
        if (newpid == 0):                                                                                                                   
            run(inst1, nRuns)
            os._exit(0)                                                                                                                     
        else:                                                                                                                               
            forkedPids.append(newpid)  
            newpid = os.fork()                                                                                                                  
            if (newpid == 0):                                                                                                                   
                run(inst2, nRuns)
                os._exit(0)                                                                                                                     
            else:                                                                                                                               
                forkedPids.append(newpid)  
    
    for p in forkedPids:                                                                                                                    
        os.waitpid(p, 0)  
    print "Finished test_manyForkedProcessesSingleThreaded"

def test_manyForkedProcessesMultiThreaded(inst1, inst2, nRuns, nProcesses, nThreads):
    print "Starting test_manyForkedProcessesMultiThreaded"
    forkedPids = []
    for i in range(nProcesses):
        newpid = os.fork()                                                                                                                  
        if (newpid == 0):                                                                                                                   
            runThreaded(inst1, inst2, nRuns, nThreads)
            os._exit(0)                                                                                                                     
        else:                                                                                                                               
            forkedPids.append(newpid)  
            newpid = os.fork()                                                                                                                  
            if (newpid == 0):                                                                                                                   
                runThreaded(inst1, inst2, nRuns, nThreads)
                os._exit(0)                                                                                                                     
            else:                                                                                                                               
                forkedPids.append(newpid)  
   
    for p in forkedPids:                                                                                                                    
        os.waitpid(p, 0)  
    print "Finished test_manyForkedProcessesMultiThreaded"


if __name__ == "__main__":
    nRuns = 1000
    nThreads = 4
    nProcesses = 4
    #Same manager, same mux
    mux = multiprocessing.Lock()
    manager = multiprocessing.Manager()
    inst1 = A(manager, mux)
    inst2 = A(manager, mux)
    print "Same manager, same mux"
    test_sameProcessSameThread(inst1, inst2, nRuns)
    test_sameProcessThreaded(inst1, inst2, nRuns, nThreads)
    test_manyProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    test_manyForkedProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    test_manyForkedProcessesMultiThreaded(inst1, inst2, nRuns, nProcesses, nThreads)

    #Different managers, different muxes
    print "Different managers, different muxes"
    mux1 = multiprocessing.Lock()
    mux2 = multiprocessing.Lock()
    manager1 = multiprocessing.managers.SyncManager()
    manager2 = multiprocessing.managers.SyncManager()
    manager1.start()
    manager2.start()
    inst1 = A(manager1, mux1)
    inst2 = A(manager2, mux2)
    test_sameProcessSameThread(inst1, inst2, nRuns)
    test_sameProcessThreaded(inst1, inst2, nRuns, nThreads)
    test_manyProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    test_manyForkedProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    test_manyForkedProcessesMultiThreaded(inst1, inst2, nRuns, nProcesses, nThreads)

    #Same manager, different muxes
    print "Same manager, different muxes"
    mux1 = multiprocessing.Lock()
    mux2 = multiprocessing.Lock()
    inst1 = A(manager, mux1)
    inst2 = A(manager, mux2)
    test_sameProcessSameThread(inst1, inst2, nRuns)
    test_sameProcessThreaded(inst1, inst2, nRuns, nThreads)
    test_manyProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    #This fails...
    #test_manyForkedProcessesSingleThreaded(inst1, inst2, nRuns, nProcesses)
    test_manyForkedProcessesMultiThreaded(inst1, inst2, nRuns, nProcesses, nThreads)

