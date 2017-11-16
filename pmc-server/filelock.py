import errno
import fcntl
import logging
import os
import select
import time

class FileLock:
    """ A (unix) file based semaphore which works based on select and file locking.
        Inspired by https://github.com/benediktschmitt/py-filelock/blob/master/filelock.py
    """

    def __init__(self, filename, globalLock):
        self.filename = filename
        self.globalLock = globalLock
        self.mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC 
        self.fd = -1

    def acquire(self):
        locked = False
        while (not locked):
            self.globalLock.acquire()
            #try to lock it
            try:
                fd = os.open(self.filename, self.mode)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                self.fd = fd
            except Exception as ex: 
                os.close(fd)
                pass
            self.globalLock.release()
            if (not locked):
                try:
                    #It was already locked. Wait for it to be unlocked
                    fd = os.open(self.filename, self.mode | os.O_APPEND)
                    r, w, e = select.select([], [fd], [], 3)
                    os.close(fd)
                    print r, w, e
                except Exception as ex: 
                    print "--->" + str(ex)
                    pass

        print "{0} locked successfully with fd {1}".format(os.getpid(), self.fd)

    def release(self):
        self.globalLock.acquire()
        print "{0} unlocking successfully with fd {1}".format(os.getpid(), self.fd)
        if (self.fd == -1):
            self.fd = os.open(self.filename, self.mode)
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)
        print "{0} unlocked successfully with fd {1}".format(os.getpid(), self.fd)
        self.globalLock.release()
