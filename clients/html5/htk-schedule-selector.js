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


import { HtkDialogs } from './htk-dialogs.js'
import * as Constants from './htk-constants.js'

const template = document.createElement('template');
template.innerHTML = `
<style>
  @import "../css/w3.css";
  @import "../css/WebFont/font-css/LineIcons.css";
</style>
<dialog id="dscheduleselector">
    <div id="divschedule">
        <table style="border-style:solid;border-width:1px;width: 100%">
            <tr>
                <td>
                    User
                </td>
                <td>
                    Schedules
                </td>
                <td>
                    Description
                </td>
            </tr>
            <tr>
                <td><select id="userselect" size="20" style="width:150px;overflow-x:scroll"></select></td>
                <td><select multiple id="scheduleselect" size="20" style="width:150px;overflow-x:scroll"></select></td>
                <td id="descriptionarea" style="width:250px;vertical-align:top;background-color:#F5F5F5"></td>
            </tr>
        </table>
        <table style="border-style:solid;border-width:0px;width: 100%">
            <tr>
                <td style="padding-top:20px;">
                    <button title="OK" id="okbtn">OK</button>
                    <button title="Cancel" id="cancelbtn">Cancel</button>
                </td>
                <td style="padding-top:20px;text-align:right;">
                    <table style="border-style:solid;border-width:0px;width: 100%">
                        <tr>
                            <td style="text-align:right;">
                                <button title="Create a new schedule..." id="createschedulebtn"><i class="lni lni-circle-plus"></i></button>
                                <button title="Create a new folder..." id="createschedulefolderbtn"><i class="lni lni-folder"></i></button>
                                <button title="Delete schedule/folder..." id="deleteschedulebtn"><i class="lni lni-circle-minus"></i></button>
                                <button title="Obsolete schedule/folder..." id="obsoleteschedulebtn"><i class="lni lni-ban"></i></button>
                                <input type="checkbox" id="showobsoletecheckbox" value="obsolete" title="Show obsolete schedules and folders?"><i class="lni lni-eye"></i></input>
                            </td>
                        </tr>
                    </table>
                </td>
           </tr>
        </table>
    </div>
    <div id="divnewschedule" hidden>
        <table style="border-style:solid;border-width:1px;width: 100%">
            <tr>
                <td>Schedule name:</td>
                <td><input type="text" id="newschedulename"></input></td>
            </tr>
            <tr>
                <td>Schedule description:</td>
                <td><textarea rows="4" cols="30" id="newscheduledescription" title="Description"></textarea></td>
            </tr>
            <tr>
                <td rowspan="2">Copy from:</td>
                <td>
                    <button title="Select" id="newschedulebtn">Select...</button>
                </td>
            </tr>
            <tr>
                <td id="newschedulescopyfromname">
                    plant
                </td>
                <td>
                    <input type="checkbox" id="inheritcheckbox" value="inherit" title="Inherit from selected schedule?">Inherit?<i class="fa fa-link"></i></input>
                </td>
            </tr>
        </table>
        <table style="border-style:solid;border-width:0px;width: 100%">
            <tr>
                <td style="padding-top:20px;">
                    <button title="OK" id="oknewschedulebtn">OK</button>
                    <button title="Cancel" id="cancelnewschedulebtn">Cancel</button>
                </td>
            </tr>
        </table>
    </div>
</dialog>
`;

/**
 * @brief A dialog which allows to select a schedule (from the ones available for this page).
 * @details This dialog allows to select an existent schedule (from this or any other Hieratika user) or to create a new schedule (for this user).
 */
export class HtkScheduleSelector extends HTMLElement {

  /**
   * @brief Constructor. NOOP.
   */
  constructor() {
    super();
  }

  /**
   * @brief Registers the dialog.
   */
  connectedCallback() {
    var templateContent = template.content;
    if (template !== undefined) {
      const root = this.attachShadow({
        mode: 'open'
      });
      root.appendChild(templateContent.cloneNode(true));
      this.pageName = "";
      this.diag = this.shadowRoot.querySelector("#dscheduleselector");
      this.userSelect = this.shadowRoot.querySelector("#userselect");
      this.userSelect.onclick = function() {
        this.okButton.disabled = true;
        this.currentFolderPath = [];
        this.updateUserSchedules();
      }.bind(this);

      this.scheduleSelect = this.shadowRoot.querySelector("#scheduleselect");
      this.scheduleSelect.onclick = function() {
        this.handleScheduleSelect();
      }.bind(this);

      this.scheduleSelect.ondblclick = function() {
        this.handleScheduleSelectDblClick();
      }.bind(this);


      this.descriptionArea = this.shadowRoot.querySelector("#descriptionarea");
      this.okButton = this.shadowRoot.querySelector("#okbtn");
      this.okButton.onclick = function() {
        var schedule = this.scheduleSelect[this.scheduleSelect.selectedIndex].scheduleInfo;
        this.okCallbackFunction(schedule);
        this.diag.close();
      }.bind(this);

      var cancelButton = this.shadowRoot.querySelector("#cancelbtn");
      cancelButton.onclick = function() {
        this.diag.close();
      }.bind(this);

      this.scheduleDiv = this.shadowRoot.querySelector("#divschedule");
      this.newScheduleDiv = this.shadowRoot.querySelector("#divnewschedule");
      this.newScheduleCopyFromName = this.shadowRoot.querySelector("#newschedulescopyfromname");
      this.newSchedulesButton = this.shadowRoot.querySelector("#newschedulebtn");
      this.newScheduleName = this.shadowRoot.querySelector("#newschedulename")
      this.newScheduleDescription = this.shadowRoot.querySelector("#newscheduledescription");
      this.copyFromScheduleUID = undefined;
      this.createNewScheduleButton = this.shadowRoot.querySelector("#createschedulebtn");
      this.createNewScheduleButton.onclick = function() {
        this.copyFromScheduleUID = undefined;
        this.scheduleDiv.setAttribute("hidden", "true");
        this.newScheduleDiv.removeAttribute("hidden");
        this.newScheduleName.value = (new Date().toISOString());
        this.newScheduleDescription.value = "Schedule created on the " + this.newScheduleName.value;
        this.newScheduleCopyFromName.innerHTML = Constants.PLANT_NAME;
        this.inheritCheckBox.disabled = true;
      }.bind(this);

      this.newScheduleSelector = undefined;
      this.copyFromScheduleUID = null;
      this.newSchedulesButton.onclick = function() {
        if (this.newScheduleSelector === undefined) {
          this.newScheduleSelector = document.createElement("htk-schedule-selector");
          this.shadowRoot.appendChild(this.newScheduleSelector);
        }
        this.newScheduleSelector.setPageName(this.pageName);
        this.newScheduleSelector.show(function(schedule) {
          this.inheritCheckBox.disabled = false;
          this.inheritCheckBox.checked = false;
          this.copyFromScheduleUID = schedule.uid;
          this.newScheduleCopyFromName.innerHTML = schedule.name + " (owner: " + schedule.owner + ")";
        }.bind(this), true, false);
      }.bind(this);

      this.deleteScheduleButton = this.shadowRoot.querySelector("#deleteschedulebtn");
      this.deleteScheduleButton.onclick = function() {
        var selectedOptions = window.htkHelper.getSelectAllSelectedValues(this.scheduleSelect);
        var selectedSchedulesUIDs = [];
        var selectedFolders = [];
        for (var i = 0; i < selectedOptions.length; i++) {
          var schedule = selectedOptions[i].scheduleInfo;
          if (schedule !== undefined) {
            selectedSchedulesUIDs.push(schedule.uid);
          }
          var folder = selectedOptions[i].folderInfo;
          if (folder !== undefined) {
            selectedFolders.push(folder.name);
          }
        }

        //var htkDialog = new HtkDialogs();

        if ((selectedSchedulesUIDs.length > 0) || (selectedFolders.length > 0)) {
          var ok = HtkDialogs.showConfirmDialog("Are you sure you want to delete the selected schedules / folders?");
          if (ok) {
            HtkDialogs.showWaitDialog();
            window.htkHelper.deleteSchedule(
              selectedSchedulesUIDs,
              function() {
                window.htkHelper.deleteScheduleFolder(
                  selectedFolders,
                  this.pageName,
                  this.currentFolderPath,
                  function() {
                    HtkDialogs.closeWaitDialog();
                    this.updateUserSchedules();
                  }.bind(this),
                  function(response) {
                    HtkDialogs.closeWaitDialog();
                    this.updateUserSchedules();
                  }.bind(this)
                );
              }.bind(this),
              function(response) {
                HtkDialogs.closeWaitDialog();
                this.updateUserSchedules();
              }.bind(this)
            );
          }
        } else {
          HtkDialogs.showErrorDialog("Please select a schedule (or folder) first");
        }
      }.bind(this);

      this.obsoleteScheduleButton = this.shadowRoot.querySelector("#obsoleteschedulebtn");
      this.obsoleteScheduleButton.onclick = function() {
        var selectedOptions = window.htkHelper.getSelectAllSelectedValues(this.scheduleSelect);
        var selectedSchedulesUIDs = [];
        var selectedFolders = [];
        for (var i = 0; i < selectedOptions.length; i++) {
          var schedule = selectedOptions[i].scheduleInfo;
          if (schedule !== undefined) {
            selectedSchedulesUIDs.push(schedule.uid);
          }
          var folder = selectedOptions[i].folderInfo;
          if (folder !== undefined) {
            selectedFolders.push(folder.name);
          }
        }
        if ((selectedSchedulesUIDs.length > 0) || (selectedFolders.length > 0)) {
          var ok = HtkDialogs.showConfirmDialog("Are you sure you want to obsolete the selected schedules / folders?");
          if (ok) {
            HtkDialogs.showWaitDialog();
            window.htkHelper.obsoleteSchedule(
              selectedSchedulesUIDs,
              function() {
                window.htkHelper.obsoleteScheduleFolder(
                  selectedFolders,
                  this.pageName,
                  this.currentFolderPath,
                  function() {
                    HtkDialogs.closeWaitDialog();
                    this.updateUserSchedules();
                  }.bind(this),
                  function(response) {
                    HtkDialogs.closeWaitDialog();
                    this.updateUserSchedules();
                  }.bind(this)
                );
              }.bind(this),
              function(response) {
                HtkDialogs.closeWaitDialog();
                this.updateUserSchedules();
              }.bind(this)
            );
          }
        } else {
          HtkDialogs.showErrorDialog("Please select a schedule (or folder) first");
        }
      }.bind(this);

      this.showObsoleteCheckBox = this.shadowRoot.querySelector("#showobsoletecheckbox");
      this.showObsoleteCheckBox.onclick = function() {
        this.updateUserSchedules();
      }.bind(this);

      this.inheritCheckBox = this.shadowRoot.querySelector("#inheritcheckbox");
      this.createNewScheduleFolderButton = this.shadowRoot.querySelector("#createschedulefolderbtn");
      this.createNewScheduleFolderButton.onclick = function() {
        var newFolderName = HtkDialogs.showInputDialog("Please insert the new folder name.");
        if (newFolderName !== null) {
          HtkDialogs.showWaitDialog();
          window.htkHelper.createScheduleFolder(
            newFolderName,
            this.pageName,
            this.currentFolderPath,
            function() {
              this.updateUserSchedules();
              HtkDialogs.closeWaitDialog();
            }.bind(this),
            function(response) {
              HtkDialogs.closeWaitDialog();
              HtkDialogs.showErrorDialog("Failed to create the schedule folder. Unknown error, check the server logs.");
            }
          );
        }
      }.bind(this);

      var cancelNewScheduleButton = this.shadowRoot.querySelector("#cancelnewschedulebtn");
      cancelNewScheduleButton.onclick = function() {
        this.scheduleDiv.removeAttribute("hidden");
        this.newScheduleDiv.setAttribute("hidden", "true");
      }.bind(this);

      var okNewScheduleButton = this.shadowRoot.querySelector("#oknewschedulebtn");
      okNewScheduleButton.onclick = function() {
        HtkDialogs.showWaitDialog();
        var sourceScheduleUID = undefined;
        var inheritFromSchedule = this.inheritCheckBox.checked;
        if (inheritFromSchedule) {
          inheritFromSchedule = "true";
        } else {
          inheritFromSchedule = "false";
        }
        if (this.copyFromScheduleUID !== undefined) {
          sourceScheduleUID = this.copyFromScheduleUID;
        }
        window.htkHelper.createSchedule(
          this.newScheduleName.value,
          this.newScheduleDescription.value,
          this.pageName,
          this.currentFolderPath,
          sourceScheduleUID,
          inheritFromSchedule,
          function() {
            this.scheduleDiv.removeAttribute("hidden");
            this.newScheduleDiv.setAttribute("hidden", "true");
            this.updateUserSchedules();
            HtkDialogs.closeWaitDialog();
          }.bind(this),
          function(response) {
            HtkDialogs.closeWaitDialog();
            HtkDialogs.showErrorDialog("Failed to create the schedule. Unknown error, check the server logs.");
          }
        );
      }.bind(this);
    }

    this.currentFolderPath = [];
    this.allowUserOK = true;
    this.allowUserScheduleManagement = true;
    this.editMode = false;
  }

  /**
   * @brief Updates the visible schedule properties against the current (schedule/folder) selection.
   */
  handleScheduleSelect() {
    if (this.userSelect.selectedIndex >= 0) {
      var username = this.userSelect[this.userSelect.selectedIndex].value;
      if (this.scheduleSelect.selectedIndex >= 0) {
        var selectedOption = this.scheduleSelect[this.scheduleSelect.selectedIndex];
        if (selectedOption.folder) {
          this.okButton.disabled = true;
        } else if (selectedOption.scheduleInfo !== undefined) {
          this.descriptionArea.innerHTML = selectedOption.scheduleInfo.description;
          var disableOK = !this.allowUserOK;
          if (this.editMode) {
            if (!disableOK) {
              var currentUsername = window.htkHelper.getUser().username;
              var userIsTheOwner = (currentUsername === username);
              disableOK = !userIsTheOwner;
            }
          }
          this.okButton.disabled = disableOK;
        }
      }
    }

  }

  /**
   * @brief Handles a double click.
   */
  handleScheduleSelectDblClick() {
    if (this.userSelect.selectedIndex >= 0) {
      var username = this.userSelect[this.userSelect.selectedIndex].value;
      if (this.scheduleSelect.selectedIndex >= 0) {
        var selectedOption = this.scheduleSelect[this.scheduleSelect.selectedIndex];
        if (selectedOption.folder) {
          if (selectedOption.value === "..") {
            this.currentFolderPath.pop();
          } else {
            this.currentFolderPath.push(selectedOption.value);
          }
          this.updateUserSchedules();
        }
      }
    }
  }

  /**
   * @brief Show only the schedules that are available for a given user.
   */
  updateUserSchedules() {
    //var htkDialog = new HtkDialogs();
    if (this.userSelect.selectedIndex >= 0) {
      HtkDialogs.showWaitDialog();
      var username = this.userSelect[this.userSelect.selectedIndex].value;
      var currentUsername = window.htkHelper.getUser().username;
      var userIsTheOwner = (currentUsername === username);
      var allowScheduleManagement = ((this.allowUserScheduleManagement) && (userIsTheOwner));
      this.createNewScheduleButton.disabled = !allowScheduleManagement;
      this.createNewScheduleFolderButton.disabled = !allowScheduleManagement;
      this.deleteScheduleButton.disabled = !allowScheduleManagement;
      this.obsoleteScheduleButton.disabled = !allowScheduleManagement;
      this.showObsoleteCheckBox.disabled = !allowScheduleManagement;
      window.htkHelper.getScheduleFolders(
        this.pageName,
        username,
        this.currentFolderPath,
        function(availableFolders) {
          this.scheduleSelect.innerHTML = "";
          if (this.currentFolderPath.length > 0) {
            var option1 = document.createElement("option");
            option1.text = "..";
            option1.value = "..";
            option1.folder = true;
            option1.style = "color:blue";
            this.scheduleSelect.appendChild(option1);
          }

          for (var i in availableFolders) {
            var folder = availableFolders[i];
            if ((!folder.obsolete) || (folder.obsolete && this.showObsoleteCheckBox.checked)) {
              var option1 = document.createElement("option");
              option1.text = folder.name;
              option1.value = folder.name;
              option1.folderInfo = folder;
              option1.obsolete = folder.obsolete;
              option1.folder = true;
              if (folder.obsolete) {
                option1.style = "color:pink";
              } else {
                option1.style = "color:blue";
              }
              this.scheduleSelect.appendChild(option1);
            }
          }

          window.htkHelper.getSchedules(
            this.pageName,
            username,
            this.currentFolderPath,
            function(availableSchedules) {
              if (availableSchedules.length === 0) {
                var atLeastOneFolder = (availableFolders.length > 0);
                if (!atLeastOneFolder) {
                  var option1 = document.createElement("option");
                  option1.text = "No schedule available...";
                  option1.value = Constants.NONE_NAME;
                  this.scheduleSelect.appendChild(option1);
                }
              } else {
                for (var i in availableSchedules) {
                  var schedule = availableSchedules[i];
                  if ((!schedule.obsolete) || (schedule.obsolete && this.showObsoleteCheckBox.checked)) {
                    var scheduleName = String(schedule.name);
                    var option1 = document.createElement("option");
                    option1.text = scheduleName;
                    option1.value = scheduleName;
                    option1.scheduleInfo = schedule;
                    option1.obsolete = schedule.obsolete;
                    option1.folder = false;
                    if (schedule.obsolete) {
                      option1.style = "color:red";
                    }
                    this.scheduleSelect.appendChild(option1);
                  }
                }

              }
              HtkDialogs.closeWaitDialog();
            }.bind(this),
            function(response) {
              HtkDialogs.closeWaitDialog();
              HtkDialogs.showErrorDialog("Failed to retrieve the schedules. Unknown error, check the server logs.");
            }
          );
        }.bind(this),
        function(response) {
          HtkDialogs.closeWaitDialog();
          HtkDialogs.showErrorDialog("Failed to retrieve the schedules. Unknown error, check the server logs.");
        }
      );
    }
  }

  /**
   * @brief Sets the new page being handled by the Hieratika UI.
   * @param[in] page the new page being displayed.
   */
  pageChanged(page) {
    this.pageName = page.name;
  }

  /**
   * @brief Sets the page name of whose schedules are to be displayed by this component.
   * @param[in] pageName the page to which the schedules are associated.
   */
  setPageName(pageName) {
    this.pageName = pageName;
  }

  /**
   * @brief Shows the dialog.
   * @param[in] okCallbackFun the function to call if the user selects OK.
   * @param[in] allowUserOK if true allows the user to select OK and change the selected schedule (otherwise it used as read-only).
   * @param[in] allowUserScheduleManagement if true allow the user to create/delete schedules.
   * @param[in] editMode if true the intention is to select a schedule for editing.
   */
  show(okCallbackFun, allowUserOK = true, allowUserScheduleManagement = true, editMode = false) {
    this.okCallbackFunction = okCallbackFun;
    this.allowUserOK = allowUserOK;
    this.allowUserScheduleManagement = allowUserScheduleManagement;
    this.okButton.disabled = true;
    this.userSelect.innerHTML = "";
    this.scheduleSelect.innerHTML = "";
    this.editMode = editMode;
    var option1 = document.createElement("option");
    option1.text = "Select user";
    option1.value = Constants.NONE_NAME;
    this.scheduleSelect.appendChild(option1);
    var allUsers = window.htkHelper.getAllUsers();
    for (var u in allUsers) {
      option1 = document.createElement("option");
      var username = allUsers[u].username;
      option1.text = username;
      option1.value = username;
      this.userSelect.appendChild(option1);
    }
    this.createNewScheduleButton.disabled = true;
    this.createNewScheduleFolderButton.disabled = true;
    this.deleteScheduleButton.disabled = true;
    this.obsoleteScheduleButton.disabled = true;
    this.showObsoleteCheckBox.disabled = true;

    this.diag.showModal();
  }
}



/**
 * @brief Registers the element.
 */
window.customElements.define('htk-schedule-selector', HtkScheduleSelector);
