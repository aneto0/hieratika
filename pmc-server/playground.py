import logging
import time
import json
logging.basicConfig(level=logging.INFO)
import multiprocessing
from xmlmanager import XmlManager
from filelock import FileLock
import os

#xmlManager = XmlManager()
#xmlManager.acquire("PATH")

#xmlManager.release("PATH")


def f(l, s):
    fl = FileLock("/tmp/a", l)
    print "Acquiring for {0}".format(os.getpid())
    fl.acquire()
    print "Acquired for {0}".format(os.getpid())
    time.sleep(10)
    print "Releasing for {0}".format(os.getpid())
    fl.release()
    print "Released for {0}".format(os.getpid())

if __name__ == '__main__':
    m = multiprocessing.Manager()
    l = multiprocessing.Lock()
    fll = FileLock("/tmp/a", l)
    fll.release()
    for i in range(2):
        multiprocessing.Process(target=f, args=(l, i)).start()



