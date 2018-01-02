import logging
import multiprocessing
import os
import random
import sys
import time
import threading
import unittest
import uuid

from hieratika.util.lockpool import LockPool
logging.basicConfig(level=logging.DEBUG)

def threadedFunction(lockPool, key, variableToProtect, sleepTime, numberOfRepeats):
    for i in range(numberOfRepeats):
        lockPool.acquire(key)
        variableToProtect.value = variableToProtect.value + 10
        time.sleep(sleepTime * random.random())
        variableToProtect.value = variableToProtect.value - 10
        lockPool.release(key)
        time.sleep(sleepTime * random.random())

def processFunction(lockPool, variablesToProtect, numberOfThreads, sleepTime = 0.5, numberOfRepeats = 5):
    threads = []
    for variable in variablesToProtect:
        for i in range(numberOfThreads):
            key = variable["key"]
            variableToProtect = variable["value"]
            t = threading.Thread(target=threadedFunction, args=(lockPool, key, variableToProtect, sleepTime, numberOfRepeats))
            threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join() 

def checkResult(variablesToProtect, expectedOutputs):
    ok = True
    for i, variable in enumerate(variablesToProtect):
        variableToProtect = variable["value"]
        expectedOutput = expectedOutputs[i]
        ok = (expectedOutput == variableToProtect.value)
    return ok

def testOneKey(numberOfProcesses, numberOfThreads, lockPoolSize = 8):
    lockPool = LockPool(lockPoolSize)
    variablesToProtect = []
    expectedOutputs = [10]
    for i, e in enumerate(expectedOutputs):
        variablesToProtect.append({"key":uuid.uuid5(uuid.NAMESPACE_OID, "KEY{0}".format(i)).hex, "value":multiprocessing.Value("i", e)})

    procs = []
    for i in range(numberOfProcesses):
        p = multiprocessing.Process(target=processFunction, args=(lockPool, variablesToProtect, numberOfThreads))
        procs.append(p)
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    ok = checkResult(variablesToProtect, expectedOutputs)
    return ok

def testManyKeys(numberOfProcesses, numberOfThreads, lockPoolSize = 8):
    lockPool = LockPool(lockPoolSize)
    lockPool2 = LockPool(lockPoolSize)
    expectedOutputs = [10, -10, 210, -210, 110]
    variablesToProtect = []
    for i, e in enumerate(expectedOutputs):
        variablesToProtect.append({"key":uuid.uuid5(uuid.NAMESPACE_OID, "KEY{0}".format(i)).hex, "value":multiprocessing.Value("i", e)})

    procs = []
    for i in range(numberOfProcesses):
        p1 = multiprocessing.Process(target=processFunction, args=(lockPool, variablesToProtect, numberOfThreads))
        p2 = multiprocessing.Process(target=processFunction, args=(lockPool2, variablesToProtect, numberOfThreads))
        procs.append(p1)
        procs.append(p2)
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    ok = checkResult(variablesToProtect, expectedOutputs)
    return ok

def testManyKeysFork(numberOfProcesses, numberOfThreads, lockPoolSize = 8):
    lockPool = LockPool(lockPoolSize)
    expectedOutputs = [10, -10, 210, -210, 110]
    variablesToProtect = []
    for i, e in enumerate(expectedOutputs):
        variablesToProtect.append({"key":"KEY{0}".format(i), "value":multiprocessing.Value("i", e)})

    forkedPids = []
    for i in range(numberOfProcesses):
        newpid = os.fork()
        if (newpid == 0):
            processFunction(lockPool, variablesToProtect, numberOfThreads)
            os._exit(0)
        else:
            forkedPids.append(newpid)
    for p in forkedPids:
        os.waitpid(p, 0)
    ok = checkResult(variablesToProtect, expectedOutputs)
    return ok

class TestLockPool(unittest.TestCase):

    def setUp(self):
        pass

    def test_oneKeyOneProcessOneThread(self):
        self.assertTrue(testOneKey(1, 1))
    
    def test_oneKeyManyProcessesOneThread(self):
        self.assertTrue(testOneKey(5, 1))

    def test_oneKeyOneProcessManyThreads(self):
        self.assertTrue(testOneKey(1, 5))

    def test_oneKeyManyProcessesManyThreads(self):
        self.assertTrue(testOneKey(5, 5))

    def test_manyKeysOneProcessOneThread(self):
        self.assertTrue(testManyKeys(1, 1))
    
    def test_manyKeysManyProcessesOneThread(self):
        self.assertTrue(testManyKeys(5, 1))

    def test_manyKeysManyProcessesOneThreadFork(self):
        self.assertTrue(testManyKeysFork(5, 1))

    def test_manyKeysOneProcessManyThreads(self):
        self.assertTrue(testManyKeys(1, 5))

    def test_manyKeysOneProcessManyThreadsFork(self):
        self.assertTrue(testManyKeysFork(1, 5))

    def test_manyKeysManyProcessesManyThreads(self):
        self.assertTrue(testManyKeys(5, 5))

    def test_manyKeysManyProcessesManyThreadsFork(self):
        self.assertTrue(testManyKeysFork(5, 2))

    def test_manyKeysManyProcessesManyThreadsUnderResourced(self):
        self.assertTrue(testManyKeys(5, 5, 4))

if __name__ == '__main__':
    unittest.main()

