import logging
import time
import json
logging.basicConfig(level=logging.INFO)
import multiprocessing
import threading
from xmlmanager import XmlManager
from lockpool import LockPool
import os
logging.basicConfig(level=logging.DEBUG)

#xmlManager = XmlManager()
#xmlManager.acquire("PATH")

#xmlManager.release("PATH")

shared1 = multiprocessing.Value("i", 0)
shared2 = multiprocessing.Value("i", 0)
shared3 = multiprocessing.Value("i", 0)
created = multiprocessing.Value("i", 0)
destroyed = multiprocessing.Value("i", 0)
lock = multiprocessing.RLock()
def f(l, m, c):
    #print "HELLO {0}-{1} {2}".format(os.getpid(),threading.current_thread().ident, created.value)
    global shared1
    global shared2
    global shared3
    global created
    global destroyed
    if (c % 2 == 0):
        shared = shared1
        key = "AKEY1"
    elif (c % 3 == 0):
        shared = shared3
        key = "AKEY3"
    else:
        shared = shared2
        key = "AKEY2"
    i = 0
    created.value = created.value + 1
    while(i < m):
        #print "Acquiring for {0}".format(os.getpid())
        l.acquire(key)
        #print "Acquired for {0}".format(os.getpid())
        shared.value = shared.value + 10
        time.sleep(10)
        shared.value = shared.value - 10
        l.release(key)
        #print "Released for {0}".format(os.getpid())
        i = i + 1
    #print "{3} {0} {1} {2}".format(os.getpid(), shared.value, i, key)
    destroyed.value = destroyed.value + 1
    #print "BYE {0}-{1} {2}".format(os.getpid(),threading.current_thread().ident, destroyed.value)

"""
    print "HELLO {0}-{1}".format(os.getpid(),threading.current_thread().ident)
    lock.acquire()
    time.sleep(2)
    lock.release()
    print "BYE {0}-{1}".format(os.getpid(),threading.current_thread().ident)
"""  

def fl(l, m, c):
    for i in range(4):
        t = threading.Thread(target=f, args=(l, m, i, ))
        t.start()
    
    while(1):
        time.sleep(1)

if __name__ == '__main__':
    l = LockPool(8)
    m = 5
    for i in range(1):
        proc = multiprocessing.Process(target=fl, args=(l, m, i, ))
        proc.start()

    while(1):
        time.sleep(1)

