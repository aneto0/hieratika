/*
 date: 27/01/2021
 author: Luca Porzio

 copyright: Copyright 2017 F4E | European Joint Undertaking for ITER and
 the Development of Fusion Energy ('Fusion for Energy').
 Licensed under the EUPL, Version 1.1 or - as soon they will be approved
 by the European Commission - subsequent versions of the EUPL (the "Licence")
 You may not use this work except in compliance with the Licence.
 You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

 warning: Unless required by applicable law or agreed to in writing,
 software distributed under the Licence is distributed on an "AS IS"
 basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 or implied. See the Licence permissions and limitations under the Licence.
*/

import HtkHelper from './htk-helper.js'

/**
* @brief Client side implementation of the SSE interface to the server.
*/
export class Stream {
  constructor() {
    this.transformationListeners = [];
  }

  /**
   * @brief Starts the SSE client interface and listens for Hieratika events.
   * @details If the received event contains a transformationUID a fireTransformationUpdated will be triggered with the updated data,
   * otherwise either the schedule or the live variables will be updated (setValue) with the most recent values.
   */
  start() {
    this.stop();
    this.evtSrc = new EventSource("/stream?token=" + HtkHelper.getToken());
    //Changed values are received in json format
    this.evtSrc.onmessage = function(e) {
      if (e.data.length > 0) {
        var jsonData = JSON.parse(e.data);
        var reset = jsonData["reset"];
        var transformationUID = jsonData["transformationUID"];
        if (reset !== undefined) {
          var tid = jsonData["tid"];
          HtkHelper.setRemoteServerTid(tid);
        } else if (transformationUID !== undefined) {
          this.fireTransformationUpdated(jsonData);
        } else {
          var variables = jsonData["variables"];
          var scheduleUID = jsonData["scheduleUID"];
          var updateLive = (jsonData["live"] !== undefined);
          var updateSchedule = (scheduleUID !== undefined);
          var updateThisSchedule = (scheduleUID === HtkHelper.getCurrentScheduleUID());
          var updatePlant = ((!updateLive) && (scheduleUID === undefined));
          //variables is a dictionary with name:value pairs
          var mainFrameHtkComponents = HtkHelper.getAllMainFrameHtkComponents();
          //If it is to update a schedule and this is not the correct uid, do not even try
          if ((updateLive) || (updateSchedule && updateThisSchedule) || (updatePlant)) {
            for (var name in variables) {
              //The same id might be used in different components
              var targetElements = mainFrameHtkComponents[name];
              var value = variables[name];
              if (targetElements !== undefined) {
                for (var i = 0; i < targetElements.length; i++) {
                  var targetElement = targetElements[i];
                  if ((updateSchedule) || (updateLive)) {
                    targetElement.setValue(value, false);
                    //Someone else changed but might not have commited!
                    HtkHelper.updateScheduleValuesToCommit(name, value);
                  } else {
                    targetElement.setPlantValue(value);
                  }
                }
              }
            }
          }
        }
      }
    }.bind(this);
  }

  /**
   * @brief Stops the SSE client interface.
   */
  stop() {
    if (this.evtSrc !== undefined) {
      this.evtSrc.close();
    }
  }

  /**
   * @brief Informs all the registered components that a transformation event as happened.
   * @param[in] transformationInfo the transformation information as a structure with the following information:
   * - "transformationUID": unique identified or the transformation;
   * - "progress": a value between 0 and 1 with the progress status;
   * - "outputs": a dictionary with the updated variable/value key-pairs.
   */
  fireTransformationUpdated(transformationInfo) {
    for (var i = 0; i < this.transformationListeners.length; i++) {
      this.transformationListeners[i].transformationUpdated(transformationInfo);
    }
  }

  /**
   * @brief Registers a component that is interested in receiving information about transformation updates.
   * @param[in] listener the component to register.
   */
  addTransformationListener(listener) {
    this.transformationListeners.push(listener);
  }
}
