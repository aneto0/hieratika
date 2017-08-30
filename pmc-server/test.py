import Queue

import threading

import epics
from epics import caget, caput, camonitor

import time

import json

from flask import Flask, Response, request

app = Flask(__name__, static_url_path="")

#Synchronised queue between the SSE stream_data function and the pvValueChanged. One queue per consumer thread. Should be further protected with semaphores
threadQueues = {}

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadQueues.iteritems():
        q.put(("pv", pvname, value), True)

#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamData():
    while True:
        tid = str(threading.current_thread())
        if tid not in threadQueues:
            threadQueues[tid] = Queue.Queue()
        monitorQueue = threadQueues[tid]
        updatedPV = monitorQueue.get(True)
        updateType = updatedPV[0]
        pvName = updatedPV[1]
        pvValue = updatedPV[2]
        encodedPy = {updateType : [ {"name" : pvName, "value" : str(pvValue)}] }
        encodedJson = json.dumps(encodedPy)
        monitorQueue.task_done()
        monitorQueue.join()
        print encodedJson 
        yield "data: {0}\n\n".format(encodedJson)

#Try to update the values in the plant
@app.route("/submit", methods=["POST", "GET"])
def submit():
    if (request.method == "GET"):
        print request.args
        for k in request.args:
            caput(k, request.args[k])
    return "done"

#Try to update the values in the plant against an existent schedule
@app.route("/changeschedule", methods=["POST", "GET"])
def changeschedule():
    if (request.method == "GET"):
        requestedSchedule = request.args["schselect"]
        with open("static/schedules.json") as jsonFile:
            schedulesJson = json.load(jsonFile)
            schedules = schedulesJson["schedules"]
            for s in schedules:
                if (s["name"] == requestedSchedule):
                    variables = s["variables"]
#                    for v in variables:
#                        if (v["isPV"] == "True"):
#                            pvName = v["name"]
#                            pvValue = v["value"]
#                            caput(pvName, pvValue)
                    break
    return json.dumps(variables)


@app.route("/stream")
def stream():
    return Response(streamData(), mimetype="text/event-stream")

@app.route("/")
def index():
    return app.send_static_file("index.html")

#List of variables to monitor
plantVariablesToMonitor = ["PMC::TEST::VAR1", "PMC::TEST::VAR2"]

if __name__ == "__main__":
    epics.ca.find_libca()
    
    for pvName in plantVariablesToMonitor:
        camonitor(pvName, None, pvValueChanged)

    app.debug = True
    app.run(threaded= True)
