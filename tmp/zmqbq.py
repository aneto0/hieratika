from broadcastqueue import BroadcastQueue 
import time
import multiprocessing
import logging
import threading
import os
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(thread)d] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')                                                         

bq = BroadcastQueue(23450)

def proc():
    while(True):
        a = bq.get()
        if a is not None:
            print "GOT IT {0}".format(a)

def putter():
    while(True):
        bq.put("CACCA"*10)
        time.sleep(1)

p1 = multiprocessing.Process(target=proc, args=( ))
p1.start()
#time.sleep(4)

p2 = multiprocessing.Process(target=putter, args=( ))
p2.start()

while(True):
    time.sleep(1)

