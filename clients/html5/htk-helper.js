/*
 date: 25/01/2021
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

/*
        <link rel="import" href="/htk-constants.html">
        <link rel="import" href="/htk-dialogs.html">
        <link rel="import" href="/htk-wait-dialog.html">
*/

import * as Constants from './htk-constants.js'
import { HtkDialogs } from './htk-dialogs.js'
import $ from './js/jquery/jquery.js'

/**
* Collection of helper functions for the hieratika client components.
*/
export class HtkHelper {

  constructor() {
    this.remoteServerTid = "";
    this.token = "";
    this.allUsers = [];
    this.invalidTokenListeners = [];
    //This reference to the main editor can be used to listen to page events for components that e.g. do not inherit from HtkComponent
    this.htkMainEditor = undefined;
    this.valuesToSynchroniseRemote = [];
    this.scheduleValuesToCommit = {};
    this.currentScheduleUID = undefined;
    this.idxx = new Date().toISOString();
  }

  /**
   * @brief Gets the UID of the schedule currently opened by the user.
   * @return the UID of the schedule currently opened by the user.
   */
  getCurrentScheduleUID() {
    return this.currentScheduleUID;
  }

  /**
   * @brief Sets the UID of the schedule currently opened by the user.
   * @param[in] scheduleUIDIn the UID of the schedule currently opened by the user.
   */
  setCurrentScheduleUID(scheduleUIDIn) {
    this.currentScheduleUID = scheduleUIDIn;
  }

  /**
   * @brief Updates the list of values that are to be commited.
   * @param[in] name the name of the variable to be (eventually commited).
   * @param[in] value the variable value.
   */
  updateScheduleValuesToCommit(name, value) {
    this.scheduleValuesToCommit[name] = value;
  }

  /**
   * @brief Resets the values that are to be commited.
   */
  resetScheduleValuesToCommit() {
    this.scheduleValuesToCommit = {};
  }

  /**
   * @brief Informs that a value is to be synchronised remote.
   * @param[in] variable the variable to synchronise.
   */
  addVariableToSynchroniseRemote(variable) {
    this.valuesToSynchroniseRemote.push(variable);
  }

  /**
   * @brief Sets the htk-main-editor (which is the owner of the main frame components).
   * @param[in] htkMainEditorIn the owner of the main frame components.
   */
  setHtkMainEditor(htkMainEditorIn) {
    this.htkMainEditor = htkMainEditorIn;
  }

  /**
   * @brief Gets the htk-main-editor (which is the owner of the main frame components).
   * @return the owner of the main frame components.
   */
  getHtkMainEditor() {
    return this.htkMainEditor;
  }

  /**
   * @brief Gets all the main frame components.
   * @return all the components that belong to the main frame.
   */
  getAllMainFrameHtkComponents() {
    return this.htkMainEditor.getAllMainFrameHtkComponents();
  }


  /**
   * @brief Registers a component that wants to informed when all the variables information, for a given page, have been loaded.
   * @param[in] listener the component to register.
   */
  addVariablesInfoLoadedListener(listener) {
    this.htkMainEditor.addVariablesInfoLoadedListener(listener);
  }

  /**
   * @brief Loads the configuration variables into the plant.
   * @details This is an asynchronous call.
   * @param[in] configName the name of the configuration that is to be load into the plant.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the variables were successfully loaded into the plant.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the variables were not loaded into the plant.
   */
  loadIntoPlant(configName, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/loadintoplant",
      data: {
        token: this.token,
        pageNames: JSON.stringify([configName])
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          if (response == "ok") {
            successFun();
          } else {
            errorFun();
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Sets the currently displayed configuration variables as the variables to be loaded into the plant (by calling loadIntoPlant).
   * @details This is an asynchronous call.
   * @param[in] configName the name of the configuration that is to be load into the plant.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the variables were successfully set as the variables to be uploaded into the plant.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the variables were not set.
   */
  updatePlant(configName, successFun, errorFun) {
    var allHtkDataJSon = {};
    //Get the values of all the HtkComponents that are displayed in the main frame.
    var mainFrameHtkComponents = this.htkMainEditor.getAllMainFrameHtkComponents();
    var keys = Object.keys(mainFrameHtkComponents);
    for (var i = 0; i < keys.length; i++) {
      var htkComp = mainFrameHtkComponents[keys[i]];
      allHtkDataJSon[htkComp[0].id] = htkComp[0].getValue();
    }
    $.ajax({
      type: "post",
      url: "/updateplant",
      data: {
        token: this.token,
        tid: this.remoteServerTid,
        pageName: configName,
        variables: JSON.stringify(allHtkDataJSon)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          if (response == "ok") {
            var htkComp;
            for (var i = 0; i < keys.length; i++) {
              //The same id can be used to store multiple instances
              var htkCompArray = mainFrameHtkComponents[keys[i]];
              for (var j = 0; j < htkCompArray.length; j++) {
                var htkComp = htkCompArray[j];
                htkComp.setInitialValue(htkComp.getValue());
              }
            }
            successFun();
          } else {
            errorFun();
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets the information (and meta information) about the provided variable names (associated to the given configuration name).
   * @details This is an asynchronous call.
   * @param[in] configName the name of the configuration that is the owner of the variables.
   * @param[in] variablesNames the name of the variables that are to be queried.
   * @param[in] successFun function with prototype (void) f(variables), that will be called if the variables were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the variables were not set.
   */
  getVariablesInfo(configName, variablesNames, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getvariablesinfo",
      data: {
        token: this.token,
        pageName: configName,
        variables: JSON.stringify(variablesNames)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          //var variables = JSON.parse(response);
          var variables = JSON.parse(response);
          successFun(variables);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets the information (and meta information) about the provided library variables names (associated to the given library type).
   * @details This is an asynchronous call.
   * @param[in] libraryType the type of library being queried.
   * @param[in] variablesNames the name of the variables that are to be queried.
   * @param[in] successFun function with prototype (void) f(variables), that will be called if the variables were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the variables were not set.
   */
  getLibraryVariablesInfo(libraryType, variablesNames, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getlibraryvariablesinfo",
      data: {
        token: this.token,
        libraryType: libraryType,
        variables: JSON.stringify(variablesNames)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var variables = JSON.parse(response);
          successFun(variables);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets the information (and meta information) about the provided live variables names.
   * @details This is an asynchronous call.
   * @param[in] variablesNames the name of the variables that are to be queried.
   * @param[in] successFun function with prototype (void) f(variables), that will be called if the variables were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the variables were not set.
   */
  getLiveVariablesInfo(variablesNames, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getlivevariablesinfo",
      data: {
        token: this.token,
        variables: JSON.stringify(variablesNames)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var variables = JSON.parse(response);
          successFun(variables);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  getScheduleVariablesValues(scheduleName, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getschedulevariablesvalues",
      data: {
        token: this.token,
        scheduleUID: scheduleName
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var variables = JSON.parse(response);
          successFun(variables);
        }
      }.bind(this),
      error: function(response) {
        console.log(response);
        alert(response);
      }.bind(this)
    });
  }

  /**
   * @brief Sets on all components the value as the plant value and sets them as read-only.
   */
  displayPlant() {
    var mainFrameHtkComponents = this.htkMainEditor.getAllMainFrameHtkComponents();
    if (mainFrameHtkComponents !== null) {
      var keys = Object.keys(mainFrameHtkComponents);
      for (var i = 0; i < keys.length; i++) {
        var htkCompArray = mainFrameHtkComponents[keys[i]];
        for (var j = 0; j < htkCompArray.length; j++) {
          var htkComp = htkCompArray[j];
          htkComp.setEditable(false);
          var value = htkComp.getPlantValue();
          if (value !== undefined) {
            htkComp.setValue(value, false);
          }
        }
      }
    }
  }

  /**
   * @brief Commits all the changes to the current schedule.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule is successfully commited.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be commited.
   */
  commitAllChangesToSchedule(successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/commitschedule",
      data: {
        token: this.token,
        tid: this.remoteServerTid,
        scheduleUID: this.currentScheduleUID,
        variables: JSON.stringify(this.scheduleValuesToCommit)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          if (response === Constants.HTK_IN_USE) {
            //var htkDialog = new HtkDialogs();
            HtkDialogs.showErrorDialog("The schedule is being used in other schedules and thus cannot be overwritten (note that it might being used by this same variable. If so unselect if first).");
            errorFun();
          } else {
            successFun();
            this.scheduleValuesToCommit = {};
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets the information about all the available pages.
   * @details This is an asynchronous call.
   * @param[in] successFun function with prototype (void) f(pages), that will be called if the pages were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the pages could not be retrieved.
   */
  getPages(successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getpages",
      data: {
        token: this.token,
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var pagesJson = JSON.parse(response);
          successFun(pagesJson);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets all the folders that belong to a given user in a given folder.
   * @param[in] configName the name of the configuration that is associated to the schedules to be retrieved.
   * @param[in] username the name of the user that owns the schedules.
   * @param[in] parentFolders full path of the folder containing the schedules to be retrieved.
   * @param[in] successFun function with prototype (void) f(folders), that will be called if the folders could be retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the folders could not be retrieved.
   */
  getScheduleFolders(configName, username, parentFolders, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getschedulefolders",
      data: {
        token: this.token,
        pageName: configName,
        username: username,
        parentFolders: JSON.stringify(parentFolders)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var availableFolders = JSON.parse(response);
          successFun(availableFolders);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }


  /**
   * @brief Gets all the schedules that belong to a given user in a given folder.
   * @param[in] configName the name of the configuration that is associated to the schedules to be retrieved.
   * @param[in] username the name of the user that owns the schedules.
   * @param[in] parentFolders full path of the folder containing the schedules to be retrieved.
   * @param[in] successFun function with prototype (void) f(schedules), that will be called if the schedules could be retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedules could not be retrieved.
   */
  getSchedules(configName, username, parentFolders, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getschedules",
      data: {
        token: this.token,
        pageName: configName,
        username: username,
        parentFolders: JSON.stringify(parentFolders)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var availableSchedules = JSON.parse(response);
          successFun(availableSchedules);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets information about a given schedule.
   * @param[in] scheduleUID the schedule unique identifier.
   * @param[in] successFun function with prototype (void) f(schedule), the function that will be called if the schedule is successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be retrieved.
   */
  getSchedule(scheduleUID, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getschedule",
      data: {
        token: this.token,
        scheduleUID: scheduleUID
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var schedule = JSON.parse(response);
          successFun(schedule);
        } else {
          errorFun(response);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Creates a new schedule.
   * @details This is an asynchronous call.
   * @param[in] scheduleName the name of the schedule to create.
   * @param[in] scheduleDescription the description of the schedule to create.
   * @param[in] configName the name of the configuration that is associated to this schedule.
   * @param[in] parentFolders full path of the folder that will contain the new schedule.
   * @param[in] sourceScheduleUID the identifier of the schedule that is being used as a basis (i.e. where to copy from) for this schedule, or undefined if it is not applicable.
   * @param[in] inheritFromSchedule if "true" the created schedule will be marked as being inherited from the sourceScheduleUID and an hardlink between the two will be created. This mean that that the sourceScheduleUID will not be modifiable nor deletable while this link exists (i.e. while the created schedule exists).
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully created.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be created.
   */
  createSchedule(scheduleName, scheduleDescription, configName, parentFolders, sourceScheduleUID, inheritFromSchedule, successFun, errorFun) {
    var schedule = {
      token: this.token,
      name: scheduleName,
      description: scheduleDescription,
      parentFolders: JSON.stringify(parentFolders),
      pageName: configName
    }
    var user = JSON.parse(localStorage.user);
    schedule["username"] = user.username;
    if (sourceScheduleUID !== undefined) {
      schedule["sourceScheduleUID"] = sourceScheduleUID;
    }
    schedule["inheritFromSchedule"] = inheritFromSchedule;
    $.ajax({
      type: "post",
      url: "/createschedule",
      data: schedule,
      success: function(response) {
        if (this.checkServerResponse(response)) {
          successFun();
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Creates a new schedule folder.
   * @details This is an asynchronous call.
   * @param[in] folderName the name of the folder to create.
   * @param[in] configName the name of the configuration that is associated to this schedule.
   * @param[in] parentFolders full path of the folder that will contain the new schedule.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully created.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be created.
   */
  createScheduleFolder(folderName, configName, parentFolders, successFun, errorFun) {
    var user = JSON.parse(localStorage.user);
    var scheduleFolder = {
      token: this.token,
      name: folderName,
      parentFolders: JSON.stringify(parentFolders),
      username: user.username,
      pageName: configName
    }
    $.ajax({
      type: "post",
      url: "/createschedulefolder",
      data: scheduleFolder,
      success: function(response) {
        if (this.checkServerResponse(response)) {
          successFun();
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Deletes an existent list of schedule folders.
   * @details This is an asynchronous call.
   * @param[in] folderName the names of the folders to delete.
   * @param[in] configName the name of the configuration that is associated to this schedule.
   * @param[in] parentFolders full path of the folder that contains the schedule.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully created.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be created.
   */
  deleteScheduleFolder(folderNames, configName, parentFolders, successFun, errorFun) {
    if (folderNames.length > 0) {
      var folderName = folderNames[0];
      var user = JSON.parse(localStorage.user);
      var scheduleFolder = {
        token: this.token,
        name: folderName,
        parentFolders: JSON.stringify(parentFolders),
        username: user.username,
        pageName: configName
      }
      $.ajax({
        type: "post",
        url: "/deleteschedulefolder",
        data: scheduleFolder,
        success: function(response) {
          if (this.checkServerResponse(response)) {
            if (response === Constants.HTK_OK) {
              folderNames.shift();
              if (folderNames.length > 0) {
                this.deleteScheduleFolder(folderNames, configName, parentFolders, successFun, errorFun);
              } else {
                successFun();
              }
            } else {
              //var htkDialog = new HtkDialogs();
              HtkDialogs.showErrorDialog("Unkown error while deleting the folder " + folderName + " in the server. Is the folder empty?. Check the logs.");
              errorFun();
            }
          }
        }.bind(this),
        error: function(response) {
          this.showCriticalError(response);
          errorFun();
        }.bind(this)
      });
    } else {
      successFun();
    }
  }

  /**
   * @brief Obsoletes an existent list of schedule folder.
   * @details This is an asynchronous call.
   * @param[in] folderNames the names of the folders to obsolete.
   * @param[in] configName the name of the configuration that is associated to this schedule.
   * @param[in] parentFolders full path of the folder that contains the schedule.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully created.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be created.
   */
  obsoleteScheduleFolder(folderNames, configName, parentFolders, successFun, errorFun) {
    if (folderNames.length > 0) {
      var folderName = folderNames[0];
      var user = JSON.parse(localStorage.user);
      var scheduleFolder = {
        token: this.token,
        name: folderName,
        parentFolders: JSON.stringify(parentFolders),
        username: user.username,
        pageName: configName
      }
      $.ajax({
        type: "post",
        url: "/obsoleteschedulefolder",
        data: scheduleFolder,
        success: function(response) {
          if (this.checkServerResponse(response)) {
            if (response === Constants.HTK_OK) {
              folderNames.shift();
              if (folderNames.length > 0) {
                this.obsoleteScheduleFolder(folderNames, configName, parentFolders, successFun, errorFun);
              } else {
                successFun();
              }
            } else {
              //var htkDialog = new HtkDialogs();
              HtkDialogs.showErrorDialog("Unkown error while obsoleting the folder " + folderName + " in the server. Check the server logs.");
              errorFun();
            }
          }
        }.bind(this),
        error: function(response) {
          this.showCriticalError(response);
          errorFun();
        }.bind(this)
      });
    } else {
      successFun();
    }
  }

  /**
   * @brief Triggers a transformation in the server.
   * @details This is an asynchronous call.
   * @param[in] funName the name of the transformationFunction.
   * @param[in] inputs the variables that are to be input to the transformation as variable/value key-pairs.
   * @param[in] successFun function with prototype (void) f(uid), that will be called if the transformation was successfully triggered.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the transformation could not be triggered.
   */
  transform(funName, inputs, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/transform",
      data: {
        token: this.token,
        fun: funName,
        inputs: JSON.stringify(inputs)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          successFun(response);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets the current logged in user.
   * @return the current logged in user.
   */
  getUser() {
    var user = localStorage.user;
    if (user !== undefined) {
      user = JSON.parse(user);
    }
    return user;
  }

  /**
   * @brief Gets all the available users.
   * @param[in] successFun function with prototype (void) f(users), that will be called if the users were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the users could not be retrieved.
   */
  getUsers(successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getusers",
      data: {
        token: this.token
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          this.allUsers = JSON.parse(response);
          successFun(this.allUsers);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Logs a user into the system.
   * @param[in] usernameToSend the username.
   * @param[in] passwordToSend the user password.
   * @param[in] successFun function with prototype (void) f(user), that will be called if the user was successfully logged in.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the user could not be logged in.
   */
  loginToServer(usernameToSend, passwordToSend, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/login",
      data: {
        username: usernameToSend,
        password: passwordToSend
      },
      success: function(response) {
        var user = JSON.parse(response);
        if (user.id !== "") {
          successFun(user);
        } else {
          errorFun();
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }
    });
  }

  /**
   * @brief Logsout a user from the system.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the user was successfully logged out.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the users could not be logged out.
   */
  logout(successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/logout",
      data: {
        token: this.token
      },
      success: function(response) {
        successFun();
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }


  /**
   * @brief Gets all the transformations associated to a given configuration.
   * @details This is an asynchronous call.
   * @param[in] configName the name of the configuration from where the transformations are to be retrieved.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully created.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be created.
   */
  getTransformations(configName, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/gettransformationsinfo",
      data: {
        token: this.token,
        pageName: configName
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var transformations = JSON.parse(response);
          successFun(transformations);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets all the available libraries (of a given type) associated to a given user.
   * @details This is an asynchronous call.
   * @param[in] libraryType the library type.
   * @param[in] username the library owner.
   * @param[in] successFun function with prototype (void) f(libraries), that will be called if the libraires were successfully retrieved .
   * @param[in] errorFun function with prototype (void) f(), that will be called if the libraries could not be retrieved.
   */
  getLibraries(libraryType, username, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getlibraries",
      data: {
        token: this.getToken(),
        type: libraryType,
        username: username,
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var libraries = JSON.parse(response);
          successFun(libraries);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets variable values of a given library instance (identified by its unique id).
   * @details This is an asynchronous call.
   * @param[in] uid the library unique identifier.
   * @param[in] successFun function with prototype (void) f(variablesValues), that will be called if the library variables values were successfully retrieved .
   * @param[in] errorFun function with prototype (void) f(), that will be called if the libraries variables values could not be retrieved.
   */
  getLibraryVariablesValues(uid, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/getlibraryvariablesvalues",
      data: {
        token: this.getToken(),
        libraryUID: uid
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var libraries = JSON.parse(response);
          successFun(libraries);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Saves a library.
   * @details This is an asynchronous call.
   * @param[in] libraryType the library type.
   * @param[in] libraryName the library name.
   * @param[in] libraryDescription the library description.
   * @param[in] variables the library variables/values key-pairs.
   * @param[in] successFun function with prototype (void) f(library), that will be called if the library was successfully saved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the libraries variables values could not be saved.
   */
  saveLibrary(libraryType, libraryName, libraryDescription, variables, successFun, errorFun) {
    var user = this.getUser();
    $.ajax({
      type: "post",
      url: "/savelibrary",
      data: {
        token: this.token,
        type: libraryType,
        name: libraryName,
        description: libraryDescription,
        username: user.username,
        variables: JSON.stringify(variables)
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          //var htkDialog = new HtkDialogs();
          if (response === Constants.HTK_IN_USE) {
            HtkDialogs.showErrorDialog("Library is being used in other schedules and thus cannot be overwritten (note that it might being used by this same variable. If so unselect if first).");
            errorFun();
          } else if (response === Constants.HTK_UNKNOWN_ERROR) {
            HtkDialogs.showErrorDialog("Unkown error while saving the library in the server");
            errorFun();
          } else {
            var library = JSON.parse(response);
            successFun(library);
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Deletes a set of schedules.
   * @details This is an asynchronous call.
   * @param[in] scheduleUID the schedule unique identifiers.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully deleted.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be deleted.
   */
  deleteSchedule(scheduleUIDs, successFun, errorFun) {
    if (scheduleUIDs.length > 0) {
      var scheduleUID = scheduleUIDs[0];
      $.ajax({
        type: "post",
        url: "/deleteschedule",
        data: {
          token: this.token,
          scheduleUID: scheduleUID
        },
        success: function(response) {
          if (this.checkServerResponse(response)) {
            if (response === Constants.HTK_OK) {
              scheduleUIDs.shift();
              if (scheduleUIDs.length > 0) {
                this.deleteSchedule(scheduleUIDs, successFun, errorFun);
              } else {
                successFun();
              }
            } else {
              //var htkDialog = new HtkDialogs();
              if (response === Constants.HTK_IN_USE) {
                HtkDialogs.showErrorDialog("Schedule " + scheduleUID + " is being used in other schedules and thus cannot be deleted.");
                errorFun();
              } else if (response === Constants.HTK_NOT_FOUND) {
                HtkDialogs.showErrorDialog("Schedule " + scheduleUID + " could not be found in the server!");
                errorFun();
              } else {
                HtkDialogs.showErrorDialog("Unkown error while deleting the schedule " + scheduleUID + " in the server");
                errorFun();
              }
            }
          }
        }.bind(this),
        error: function(response) {
          this.showCriticalError(response);
          errorFun();
        }.bind(this)
      });
    } else {
      successFun();
    }
  }

  /**
   * @brief Obsoletes a set of schedules.
   * @details This is an asynchronous call.
   * @param[in] scheduleUID the schedule unique identifiers.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the schedule was successfully obsoleted.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the schedule could not be obsoleted.
   */
  obsoleteSchedule(scheduleUIDs, successFun, errorFun) {
    if (scheduleUIDs.length > 0) {
      var scheduleUID = scheduleUIDs[0];
      $.ajax({
        type: "post",
        url: "/obsoleteschedule",
        data: {
          token: this.token,
          scheduleUID: scheduleUID
        },
        success: function(response) {
          if (this.checkServerResponse(response)) {
            if (response === Constants.HTK_OK) {
              scheduleUIDs.shift();
              if (scheduleUIDs.length > 0) {
                this.obsoleteSchedule(scheduleUIDs, successFun, errorFun);
              } else {
                successFun();
              }
            } else {
              //var htkDialog = new HtkDialogs();
              if (response === Constants.HTK_NOT_FOUND) {
                HtkDialogs.showErrorDialog("Schedule " + scheduleUID + " could not be found in the server!");
                errorFun();
              } else {
                HtkDialogs.showErrorDialog("Unkown error while obsoleting the schedule " + scheduleUID + " in the server");
                errorFun();
              }
            }
          }
        }.bind(this),
        error: function(response) {
          this.showCriticalError(response);
          errorFun();
        }.bind(this)
      });
    } else {
      successFun();
    }
  }


  /**
   * @brief Deletes a library.
   * @details This is an asynchronous call.
   * @param[in] libraryUID the library unique identifier.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the library was successfully deleted.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the library could not be deleted.
   */
  deleteLibrary(libraryUID, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/deletelibrary",
      data: {
        token: this.token,
        libraryUID: libraryUID
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          if (response === Constants.HTK_OK) {
            successFun();
          } else {
            //var htkDialog = new HtkDialogs();
            if (response === Constants.HTK_IN_USE) {
              HtkDialogs.showErrorDialog("Library is being used in other schedules and thus cannot be deleted.");
              errorFun();
            } else if (response === Constants.HTK_NOT_FOUND) {
              HtkDialogs.showErrorDialog("Library could not be found in the server!");
              errorFun();
            } else {
              HtkDialogs.showErrorDialog("Unkown error while deleting the library in the server");
              errorFun();
            }
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Obsoletes a library.
   * @details This is an asynchronous call.
   * @param[in] libraryUID the library unique identifier.
   * @param[in] successFun function with prototype (void) f(void), that will be called if the library was successfully obsoleted.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the library could not be obsoleted.
   */
  obsoleteLibrary(libraryUID, successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/obsoletelibrary",
      data: {
        token: this.token,
        libraryUID: libraryUID
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          if (response === Constants.HTK_OK) {
            successFun();
          } else {
            //var htkDialog = new HtkDialogs();
            if (response === Constants.HTK_NOT_FOUND) {
              HtkDialogs.showErrorDialog("Library could not be found in the server!");
              errorFun();
            } else {
              HtkDialogs.showErrorDialog("Unkown error while obsoleting the library in the server");
              errorFun();
            }
          }
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }

  /**
   * @brief Gets statistics information regarding the system performance.
   * @details This is an asynchronous call.
   * @param[in] successFun function with prototype (void) f(statistics), that will be called if the variables were successfully retrieved.
   * @param[in] errorFun function with prototype (void) f(), that will be called if the statistics could not be retrieved.
   */
  getStatistics(successFun, errorFun) {
    $.ajax({
      type: "post",
      url: "/statistics",
      data: {
        token: localStorage.currentToken
      },
      success: function(response) {
        if (this.checkServerResponse(response)) {
          var statistics = JSON.parse(response);
          successFun(statistics);
        }
      }.bind(this),
      error: function(response) {
        this.showCriticalError(response);
        errorFun();
      }.bind(this)
    });
  }


  /**
   * @brief Checks if the response from the server is valid (i.e. if the server has not replied with HTK_INVALID_TOKEN). If it returned with HTK_INVALID_TOKEN calls fireInvalidToken().
   * @return true if the response from the server is not HTK_INVALID_TOKEN.
   */
  checkServerResponse(response) {
    var ok = (response.length > 0);
    if (ok) {
      if (response === Constants.HTK_INVALID_TOKEN) {
        ok = false;
        this.fireInvalidToken();
      }
    }
    return ok;
  }

  /**
   * @brief Registers a component that is interested in being notified if an HTK_INVALID_TOKEN is received from the server.
   */
  addInvalidTokenListener(listener) {
    this.invalidTokenListeners.push(listener);
  }

  /**
   * @brief Informs all the registered components that an invalid token was received from the server.
   */
  fireInvalidToken() {
    for (var l in this.invalidTokenListeners) {
      this.invalidTokenListeners[l].invalidTokenReceived();
    }
  }

  /**
   * @brief Updates the schedule remotely with any values that have changed in the last period.
   */
  synchroniseRemote() {
    //This is because in the context of the setInterval callback the this is the Window
    var _this = htkHelper;
    if (_this.currentScheduleUID !== undefined) {
      var toPop = _this.valuesToSynchroniseRemote.length;
      if (toPop > 0) {
        var variablesToSend = {};
        //Not perfectly safe, but worst comes to the worst I send twice the same thing from time to time
        var i = 0;
        while (i < toPop) {
          var valueToSynch = _this.valuesToSynchroniseRemote.shift(); //not pop since we want to remove the oldest (i.e. the first) before
          variablesToSend[valueToSynch.id] = valueToSynch.value;
          _this.scheduleValuesToCommit[valueToSynch.id] = valueToSynch.value;
          i++;
        }
        $.ajax({
          type: "post",
          url: "/updateschedule",
          data: {
            token: _this.token,
            tid: _this.remoteServerTid,
            scheduleUID: _this.currentScheduleUID,
            variables: JSON.stringify(variablesToSend)
          },
          success: function(response) {}.bind(_this),
          error: function(response) {
            console.log(response);
            alert(response);
          }.bind(_this)
        });
      }
    }
  }

  /**
   * @brief Attemps to cast the input text into the appropriate typed value.
   * @param[in] txtValue the text to be casted.
   * @param[in] typeValue the type of the value to be casted.
   * @return the casted value if successful or, otherwise, the original text.
   */
  textToTypeValue(txtValue, typeValue) {
    var ret = txtValue;
    if (typeValue !== undefined) {
      if (typeValue.startsWith("float")) {
        if (!isNaN(ret)) {
          ret = parseFloat(ret);
        } else {
          ret = undefined;
        }
      } else if ((typeValue.startsWith("int") || (typeValue.startsWith("uint")))) {
        if (!isNaN(ret)) {
          ret = parseFloat(ret);
          if (Number.isInteger(ret)) {
            ret = parseInt(ret);
          } else {
            ret = undefined;
          }
        } else {
          ret = undefined;
        }
      }
    }
    return ret;
  }

  /**
   * @brief Sets the thread identifier on the remote server which is sending events through the SSE. This is to avoid receiving updates from ourselves.
   * @param[in] remoteServerTidIn the thread identifier on the remote server.
   */
  setRemoteServerTid(remoteServerTidIn) {
    this.remoteServerTid = remoteServerTidIn;
  }

  /**
   * @brief Gets the authentication token that is being used to communicate with the server.
   */
  getToken() {
    return this.token;
  }

  /**
   * @brief Sets the authentication token that is being to communicate with the server.
   * @param[in] tokenIn the token to set.
   */
  setToken(tokenIn) {
    this.token = tokenIn;
    localStorage.currentToken = this.token;
  }

  /**
   * @brief Alert to be shown when there is a critical error communicating with the server.
   */
  showCriticalError(err) {
    //var htkDialog = new HtkDialogs();
    HtkDialogs.showErrorDialog("Critical error communicating with the server." + err);
  }

  /**
   * @brief Gets all the available users.
   * @return all the available users.
   */
  getAllUsers() {
    return this.allUsers;
  }

  /**
   * @brief Helper function which gets all the selected options in any select (with or without multiple).
   * @param[in] select the HTML select where to get the options from.
   * @return all the selected options.
   */
  getSelectAllSelectedValues(select) {
    var result = [];
    var options = select && select.options;
    var nOptions = options.length;
    for (var i = 0; i < nOptions; i++) {
      var opt = options[i];
      if (opt.selected) {
        result.push(opt);
      }
    }
    return result;
  }
}