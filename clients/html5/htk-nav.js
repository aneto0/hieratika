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
        /*
        <link rel="import" href="/libraries.html">
        <link rel="import" href="/htk-helper.html">
        <link rel="import" href="/htk-login.html">
        <link rel="import" href="/htk-main-editor.html">
        <link rel="import" href="/htk-page-selector.html">
        <link rel="import" href="/htk-schedule-selector.html">
        <link rel="import" href="/htk-stream.html">
        <link rel="import" href="/htk-transformations.html">
        */


;
import { HtkDialogs } from './htk-dialogs.js';
import { Stream } from './htk-stream.js';
import * as Constants from './htk-constants.js';

const template = document.createElement('template');
template.innerHTML = `
<style>
  @import "./css/w3.css";
  @import "./css/WebFont/font-css/LineIcons.css";
</style>
    <div class="w3-sidebar w3-bar-block w3-dark-grey w3-animate-left w3-large" style="display:none" id="tsidebar">
        <button class="w3-bar-item w3-button w3-tiny w3-light-grey" id="tsidebarclose"><i class="lni lni-arrow-left"></i></button>
        <button class="w3-bar-item w3-button w3-border-bottom" id="loginbtn"><i class="lni lni-user"> Login</i></button>
        <button href="#" class="w3-bar-item w3-button w3-border-bottom" title="Set the current page" id="pageselectbtn"><i class="lni lni-ticket-alt"> Open</i></button>
        <button class="w3-button w3-block w3-left-align" id="tviewaccbtn"><i class="lni lni-magnifier"></i> View <i class="lni lni-chevron-down"></i></button>
        <div id="tviewacc" class="w3-hide w3-green w3-card">
            <button class="w3-bar-item w3-button w3-text-white" title="View the plant" id="viewplantbtn"><i class="lni lni-skipping-rope"></i> Plant</button>
            <button class="w3-bar-item w3-button w3-text-white" title="Edit a schedule" id="viewschedulebtn"><i class="lni lni-control-panel"></i> Schedule</button>
        </div>
        <button class="w3-bar-item w3-button w3-border-bottom" id="editschedulebtn"><i class="lni lni-pencil"></i> Edit</button>
        <button class="w3-button w3-block w3-left-align" id="trefaccbtn"><i class="lni lni-baloon"></i> Compare <i class="lni lni-chevron-down"></i></button>
        <div id="trefacc" class="w3-hide w3-green w3-card">
            <button class="w3-bar-item w3-button w3-text-white" title="Remove the reference" id="refselectnonebtn"><i class="lni lni-cross-circle" style="color:#cc0000;"></i> Remove</button>
            <button class="w3-bar-item w3-button w3-text-white" title="Set the plant as the reference" id="refselectplantbtn"><i class="lni lni-skipping-rope"></i> Plant</button>
            <button class="w3-bar-item w3-button w3-text-white" title="Set another schedule as the reference" id="refselectschedulebtn"><i class="lni lni-control-panel"></i> Schedule</button>
        </div>
        <button class="w3-button w3-block w3-left-align" id="tcpyaccbtn"><i class="lni lni-files"></i> Copy <i class="lni lni-chevron-down"></i></button>
        <div id="tcpyacc" class="w3-hide w3-green w3-card">
            <button class="w3-bar-item w3-button w3-text-white" title="Copy from the plant" id="cpyreferenceplantbtn"><i class="lni lni-skipping-rope"></i> Plant</button>
            <button class="w3-bar-item w3-button w3-text-white" title="Copy from a given schedule" id="cpyreferenceschedulebtn"><i class="lni lni-control-panel"></i> Schedule</button>
        </div>
        <button class="w3-bar-item w3-button w3-border-top" title="Commit all changes to current schedule" id="commitbtn"><i class="lni lni-save"></i> Commit</button>
        <button class="w3-bar-item w3-button" title="Undo all changes" id="undobtn"><i class="lni lni-spinner-arrow"></i> Undo</button>
        <button class="w3-bar-item w3-button" title="Set current values as the plant" id="setplantbtn"><i class="lni lni-skipping-rope"></i> Set plant</button>
        <button class="w3-bar-item w3-button w3-border-top" title="Manage transformations" id="transformationsbtn"><i class="lni lni-ruler-pencil"></i> f(x)</button>
        <button class="w3-bar-item w3-button w3-border-top" title="Load the current plant into the system" id="loadintoplantbtn"><i class="lni lni-upload"></i> Load</button>
        <button class="w3-bar-item w3-button w3-border-top" title="Show system statistics" id="showstatisticsbtn"><i class="lni lni-bar-chart"></i> Statistics</button>
        <button class="w3-bar-item w3-button w3-border-top w3-blue" title="Create new plant configuration" id="plantbuilder"><i class="lni lni-grid"></i> Plant Builder</button>
    </div>
    <div class="w3-bar w3-dark-grey w3-tiny">
        <button class="w3-button" id="tsidebaropen">&#9776;</button>
        <span class="w3-bar-item w3-right" id="currentdisplay">None</span>
        <span class="w3-bar-item w3-right w3-border-left">Displaying: </span>
        <span class="w3-bar-item w3-right" id="currentreference">None</span>
        <span class="w3-bar-item w3-right w3-border-left">Reference: </span>
        <span class="w3-bar-item w3-right" id="username">(login first)</span>
        <span class="w3-bar-item w3-right w3-border-left">Username: </span>
    </div>
    <htk-login id="htklogin"></htk-login>
    <htk-page-selector id="pageselector"></htk-page-selector>
    <htk-schedule-selector id="scheduleselector"></htk-schedule-selector>
    <htk-transformations id="transformations"></htk-transformations>
`;

                /**
                 * @brief Hieratika navigation panel.
                 */
                class HtkNav extends HTMLElement {

                    /**
                     * @brief Constructor. NOOP.
                     */
                    constructor() {
                        super();
                        //HtkDialog = new HtkDialogs();
                    }

                    /**
                     * @brief See HTMLElement.createdCallback.
                     */
                    connectedCallback () {
                        var templateContent = template.content;
                        const root = this.attachShadow({mode: 'open'});
                        root.appendChild(templateContent.cloneNode(true));

                        this.sideBar = this.shadowRoot.querySelector("#tsidebar");
                        var sideBarOpen = this.shadowRoot.querySelector("#tsidebaropen");
                        var sideBarClose = this.shadowRoot.querySelector("#tsidebarclose");
                        sideBarOpen.onclick = function(evt) {
                            this.sideBar.style.display = "block";
                        }.bind(this);

                        sideBarClose.onclick = function() {
                            this.hideSideBar();
                        }.bind(this);

                        var viewAccordion = this.shadowRoot.querySelector("#tviewacc");
                        var viewAccordionButton = this.shadowRoot.querySelector("#tviewaccbtn");
                        viewAccordionButton.onclick = function() {
                            this.handleAccordionClick(viewAccordion);
                        }.bind(this);

                        var refAccordion = this.shadowRoot.querySelector("#trefacc");
                        var refAccordionButton = this.shadowRoot.querySelector("#trefaccbtn");
                        refAccordionButton.onclick = function() {
                            this.handleAccordionClick(refAccordion);
                        }.bind(this);

                        var copyAccordion = this.shadowRoot.querySelector("#tcpyacc");
                        var copyAccordionButton = this.shadowRoot.querySelector("#tcpyaccbtn");
                        copyAccordionButton.onclick = function() {
                            this.handleAccordionClick(copyAccordion);
                        }.bind(this);

                        this.setPlantButton = this.shadowRoot.querySelector("#setplantbtn");
                        this.setPlantButton.onclick = function() {
                            this.hideSideBar();
                            HtkDialogs.showWaitDialog();
                            window.htkHelper.updatePlant(this.selectedPage.name, this.updatePlantCompleted, this.updatePlantError);
                        }.bind(this);

                        this.loadIntoPlantButton = this.shadowRoot.querySelector("#loadintoplantbtn");
                        this.loadIntoPlantButton.onclick = function() {
                            this.hideSideBar();
                            HtkDialogs.showWaitDialog();
                            window.htkHelper.loadIntoPlant(this.selectedPage.name, this.loadIntoPlantCompleted, this.loadIntoPlantError);
                        }.bind(this);

                        this.showStatisticsButton = this.shadowRoot.querySelector("#showstatisticsbtn");
                        this.showStatisticsButton.onclick = function() {
                            this.hideSideBar();
                            window.htkHelper.getHtkMainEditor().showStatistics();
                        }.bind(this);

                        this.showPlantBuilderButton = this.shadowRoot.querySelector("#plantbuilder");
                        this.showPlantBuilderButton.onclick = function() {
                            this.hideSideBar();
                            window.htkHelper.getHtkMainEditor().showPlantBuilder();
                        }.bind(this);

                        this.pageSelectButton = this.shadowRoot.querySelector("#pageselectbtn");
                        this.loginButton = this.shadowRoot.querySelector("#loginbtn");
                        this.loginDialog = this.shadowRoot.querySelector("#htklogin");
                        this.loginDialog.addLoginListener(this);
                        this.loginButton.onclick = function() {
                            this.hideSideBar();
                            var user = window.htkHelper.getUser();
                            if (user === undefined) {
                                this.loginDialog.show();
                            }
                            else {
                                this.fireUserLogout();
                            }
                        }.bind(this);

                        this.standalone = this.getAttribute("data-standalone");
                        if (this.standalone !== undefined) {
                            this.standalone = (this.standalone.toLowerCase() === "true");
                        }
                        else {
                            this.standalone = false;
                        }
                        if (!this.standalone) {
                            this.streamer = new Stream();
                        }
                        this.loginButton.disabled = this.standalone;

                        this.pageSelector = this.shadowRoot.querySelector("#pageselector");
                        this.pageSelectButton.onclick = function() {
                            this.hideSideBar();
                            window.htkHelper.setCurrentScheduleUID(undefined);
                            this.pageSelector.show(this.firePageChanged.bind(this));
                        }.bind(this);

                        this.scheduleSelector = this.shadowRoot.querySelector("#scheduleselector");
                        this.editScheduleButton = this.shadowRoot.querySelector("#editschedulebtn");
                        this.editScheduleButton.onclick = function() {
                            this.hideSideBar();
                            this.scheduleSelector.show(this.editScheduleChanged.bind(this), true, true, true);
                        }.bind(this);

                        this.viewScheduleButton = this.shadowRoot.querySelector("#viewschedulebtn");
                        this.viewScheduleButton.onclick = function() {
                            this.hideSideBar();
                            this.handleAccordionClick(viewAccordion);
                            this.scheduleSelector.show(this.viewScheduleChanged.bind(this));
                        }.bind(this);

                        this.viewPlantButton = this.shadowRoot.querySelector("#viewplantbtn");
                        this.viewPlantButton.onclick = function() {
                            this.hideSideBar();
                            this.handleAccordionClick(viewAccordion);
                            window.htkHelper.setCurrentScheduleUID(undefined);
                            this.currentDisplay.innerHTML = Constants.PLANT_NAME;
                            this.setPlantButton.disabled = true;
                            this.copyFromReferenceScheduleButton.disabled = true;
                            this.copyFromReferencePlantButton.disabled = true;
                            this.commitButton.disabled = true;
                            this.undoButton.disabled = true;
                            window.htkHelper.displayPlant();
                        }.bind(this);

                        this.usernameDisplay = this.shadowRoot.querySelector("#username");
                        this.currentDisplay = this.shadowRoot.querySelector("#currentdisplay");
                        this.currentReference = this.shadowRoot.querySelector("#currentreference");

                        var user = window.htkHelper.getUser();
                        if (user === undefined) {
                            this.loginButton.value = "<i class='fas fa-user-o'> Login</i>";
                        }
                        else {
                            window.htkHelper.setToken(localStorage.currentToken);
                            this.loginSuccessful(user);
                        }
                        this.pageSelect = this.shadowRoot.querySelector("#pageselect");

                        this.referenceSelectNoneButton = this.shadowRoot.querySelector("#refselectnonebtn");
                        this.referenceSelectNoneButton.onclick = function () {
                            this.hideSideBar();
                            this.handleAccordionClick(refAccordion);
                            this.setReference(Constants.NONE_NAME);
                            this.currentReference.innerHTML = Constants.NONE_NAME;
                            this.currentReference.style.color = Constants.NONE_COLOR;
                        }.bind(this);

                        this.referenceSelectPlantButton = this.shadowRoot.querySelector("#refselectplantbtn");
                        this.referenceSelectPlantButton.onclick = function () {
                            this.hideSideBar();
                            this.handleAccordionClick(refAccordion);
                            this.setReference(Constants.PLANT_NAME);
                            this.currentReference.innerHTML = Constants.PLANT_NAME;
                        }.bind(this);

                        this.referenceSelectScheduleButton = this.shadowRoot.querySelector("#refselectschedulebtn");
                        this.referenceSelectScheduleButton.onclick = function () {
                            this.hideSideBar();
                            this.handleAccordionClick(refAccordion);
                            this.scheduleSelector.show(this.refererenceScheduleChanged.bind(this));
                        }.bind(this);

                        this.copyFromReferenceScheduleButton = this.shadowRoot.querySelector("#cpyreferenceschedulebtn");
                        this.copyFromReferenceScheduleButton.onclick = function () {
                            this.hideSideBar();
                            this.handleAccordionClick(copyAccordion);
                            this.scheduleSelector.show(this.copyFromScheduleChanged.bind(this));
                        }.bind(this);

                        this.copyFromReferencePlantButton = this.shadowRoot.querySelector("#cpyreferenceplantbtn");
                        this.copyFromReferencePlantButton.onclick = function () {
                            this.hideSideBar();
                            this.handleAccordionClick(copyAccordion);
                            var mainFrameHtkComponents = window.htkHelper.getAllMainFrameHtkComponents();
                            var keys = Object.keys(mainFrameHtkComponents);
                            for (var i=0; i<keys.length; i++) {
                                var htkCompArray = mainFrameHtkComponents[keys[i]];
                                for (var j=0; j<htkCompArray.length; j++) {
                                    var htkComp = htkCompArray[j];
                                    htkComp.setValue(htkComp.getPlantValue());
                                }
                            }
                        }.bind(this);


                        this.commitButton = this.shadowRoot.querySelector("#commitbtn");
                        this.commitButton.onclick = function () {
                            this.hideSideBar();
                            HtkDialogs.showWaitDialog();
                            window.htkHelper.commitAllChangesToSchedule(this.commitCompleted, this.commitError);
                        }.bind(this);

                        this.undoButton = this.shadowRoot.querySelector("#undobtn");
                        this.undoButton.onclick = function () {
                            this.hideSideBar();
                            this.undoAllChangesToSchedule();
                        }.bind(this);

                        this.transformationsViewer = this.shadowRoot.querySelector("#transformations");
                        this.transformationsButton = this.shadowRoot.querySelector("#transformationsbtn");
                        this.transformationsButton.onclick = function() {
                            this.transformationsViewer.show();
                        }.bind(this);

                        if(!this.standalone){
                            this.streamer.addTransformationListener(this.transformationsViewer);
                        }

                        window.htkHelper.setHtkNav(this);
                        window.htkHelper.addInvalidTokenListener(this);
                        this.pageListeners = [this];
                        this.scheduleChangeListeners = [this];
                        this.userLogoutListeners = [this];
                        this.addPageListener(this.scheduleSelector);
                        this.disableAllButPageSelect();

                        if (this.standalone) {
                            window.htkHelper.loginToServer("", "", this.loginSuccessful.bind(this), this.loginError.bind(this));
                        }
                    }


                    /**
                     * @brief See HTMLElement.attachedCallback.
                     */
                    adoptedCallback() {
                        if (this.standalone) {
                            window.htkHelper.loginToServer("", "", this.loginSuccessful.bind(this), this.loginError.bind(this));
                        }
                    }

                    /**
                     * @brief Callback function that is called when the load of the variables into the plant has been (asynchronously) completed successfully.
                     */
                    loadIntoPlantCompleted() {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showInformationDialog("Plant loaded successfully");
                    }

                    /**
                     * @brief Callback function that is called when the load of the variables into the plant has been (asynchronously) completed with an error.
                     */
                    loadIntoPlantError() {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showErrorDialog("Failed to load the values into the plant. Unknown error, check the server logs.");
                    }

                    /**
                     * @brief Callback function that is called when the update of the variables into the plant has been (asynchronously) completed successfully.
                     */
                    updatePlantCompleted() {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showInformationDialog("Plant updated successfully. Do not forget to load.");
                    }

                    /**
                     * @brief Callback function that is called when the update of the variables into the plant has been (asynchronously) completed with an error.
                     */
                    updatePlantError() {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showErrorDialog("Failed to update plant values. Unknown error, check the server logs.");
                    }

                    /**
                     * @brief Callback function that is called when the commit of the variables into the schedule has been (asynchronously) completed successfully.
                     */
                    commitCompleted() {
                        var mainFrameHtkComponents = window.htkHelper.getAllMainFrameHtkComponents();
                        var keys = Object.keys(mainFrameHtkComponents);
                        for (var i=0; i<keys.length; i++) {
                            var htkCompArray = mainFrameHtkComponents[keys[i]];
                            for (var j=0; j<htkCompArray.length; j++) {
                                var htkComp = htkCompArray[j];
                                htkComp.setInitialValue(htkComp.getValue());
                            }
                        }
                        HtkDialogs.closeWaitDialog();
                    }

                    /**
                     * @brief Callback function that is called when the commit of the variables into the schedule has been (asynchronously) completed with an error.
                     */
                    commitError() {
                        HtkDialogs.closeWaitDialog();
                    }

                    /**
                     * @brief Helper function to show/hide the accordion pane.
                     */
                    handleAccordionClick(acc) {
                        if (acc.className.indexOf("w3-show") == -1) {
                            acc.className += " w3-show";
                        } else {
                            acc.className = acc.className.replace(" w3-show", "");
                        }
                    }

                    /**
                     * @brief Hides the navigation pane.
                     */
                    hideSideBar() {
                        this.sideBar.style.display = "none";
                    }

                    /**
                     * @brief Callback function that is called when all the variables have been loaded.
                     * @details Enables the buttons that allow to interact with the variables.
                     */
                    variablesInfoLoaded() {
                        this.referenceSelectScheduleButton.disabled = false;
                        this.referenceSelectNoneButton.disabled = false;
                        this.referenceSelectPlantButton.disabled = false;
                        this.currentDisplay.innerHTML = Constants.PLANT_NAME;
                    }

                    /**
                     * @brief Callback function that is called when a user has been successfully logged in.
                     * @details Starts the HtkStream and allows the user to interact with the system.
                     */
                    loginSuccessful(user) {
                        if(!this.standalone){
                          this.user = user;
                        }
                        window.htkHelper.getUsers(
                            function (allUsers) {
                                if(!this.standalone){
                                    this.streamer.start();
                                    this.usernameDisplay.innerHTML = this.user.username;
                                    this.usernameDisplay.title = "username: " + this.user.username;
                                    this.loginButton.innerHTML = "<i class='fas fa-user-o'> Logout</i>";
                                }
                                else {
                                  this.usernameDisplay.innerHTML = allUsers[0].username;
                                  this.usernameDisplay.title = "username: " + allUsers[0].username;
                                  this.loginButton.innerHTML = "<i class='fas fa-user-o'> Logout</i>";
                                  localStorage.user = JSON.stringify(allUsers[0]);
                                }
                                this.pageSelectButton.disabled = false;
                            }.bind(this),
                            function (response) {
                                console.log(response);
                                alert(response);
                            }
                        );
                    }

                    /**
                     * @brief Informs all registered components that a new schedule has been selected to be displayed.
                     * @param[in] schedule the schedule that was selected.
                     */
                    fireScheduleChanged(schedule) {
                        for(var l in this.scheduleChangeListeners) {
                            this.scheduleChangeListeners[l].scheduleChanged(schedule);
                        }
                    }

                    /**
                     * @brief Informs all registered components that a new page has been selected.
                     * @param[in] page the page that was selected.
                     */
                    firePageChanged(page) {
                        for(var l in this.pageListeners) {
                            this.pageListeners[l].pageChanged(page);
                        }
                    }

                    /**
                     * @brief Informs all registered components that a user was logged out.
                     */
                    fireUserLogout() {
                        for(var l in this.userLogoutListeners) {
                            this.userLogoutListeners[l].userLogout();
                        }
                    }

                    /**
                     * @brief Callback function which is called when an invalid token is received from the server.
                     */
                    invalidTokenReceived() {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showErrorDialog("You have been logged out from the server. Please login again.");
                        this.fireUserLogout();
                    }

                    loginError() {
                      HtkDialogs.showErrorDialog("Error during login. Please try again.");
                    }

                    /**
                     * @brief Logsout a user from the system and disables the buttons that allow to interact with the system.
                     */
                    userLogout() {
                        window.htkHelper.logout(
                            function() {
                                localStorage.removeItem("user");
                                localStorage.removeItem("schedule");
                                this.usernameDisplay.innerHTML = "(login first)"
                                this.currentDisplay.innerHTML = Constants.NONE_NAME;
                                this.currentDisplay.style.color = Constants.NONE_COLOR;
                                this.currentReference.innerHTML = Constants.NONE_NAME;
                                this.currentReference.style.color = Constants.NONE_COLOR;
                                this.loginButton.innerHTML = "<i class='fas fa-user-o'> Login</i>";
                                this.pageSelectButton.disabled = true;
                                this.disableAllButPageSelect();
                                if (!this.standalone) {
                                    this.streamer.stop();
                                }
                            }.bind(this),
                            function() {
                            }
                        );
                    }

                    /**
                     * @brief Disables all the buttons, but the one that allows to load a new page.
                     */
                    disableAllButPageSelect() {
                        this.setPlantButton.disabled = true;
                        this.loadIntoPlantButton.disabled = true;
                        this.editScheduleButton.disabled = true;
                        this.transformationsButton.disabled = true;
                        this.viewPlantButton.disabled = true;
                        this.viewScheduleButton.disabled = true;
                        this.copyFromReferenceScheduleButton.disabled = true;
                        this.copyFromReferencePlantButton.disabled = true;
                        this.referenceSelectScheduleButton.disabled = true;
                        this.referenceSelectNoneButton.disabled = true;
                        this.referenceSelectPlantButton.disabled = true;
                        this.commitButton.disabled = true;
                        this.undoButton.disabled = true;
                    }

                    /**
                     * @brief Gets all the transformations that are available for a given page.
                     */
                    getTransformations() {
                        HtkDialogs.showWaitDialog();
                        window.htkHelper.getTransformations(
                            this.selectedPage.name,
                            function (transformations) {
                                this.transformationsViewer.setTransformations(transformations);
                                this.editScheduleButton.disabled = false;
                                this.loadIntoPlantButton.disabled = false;
                                this.transformationsButton.disabled = false;
                                this.viewScheduleButton.disabled = false;
                                this.viewPlantButton.disabled = false;
                                this.referenceSelectScheduleButton.disabled = false;
                                this.referenceSelectNoneButton.disabled = false;
                                this.referenceSelectPlantButton.disabled = false;
                                HtkDialogs.closeWaitDialog();
                            }.bind(this),
                            function (response) {
                                HtkDialogs.closeWaitDialog();
                                HtkDialogs.showErrorDialog("Failed to getTransformations. Unknown error, check the server logs.");
                            }
                        );
                    }

                    /**
                     * @brief Callback function that is called when a user selects a different page.
                     * @param[in] page the page that was selected by the user.
                     */
                    pageChanged(page) {
                        this.selectedPage = page;
                        this.getTransformations();
                    }

                    /**
                     * @brief Callback function that is called when a user selects a different schedule to be displayed.
                     * @param[in] schedule the schedule that was selected by the user.
                     */
                    scheduleChanged(schedule) {
                        var currentScheduleText = schedule.name;
                        this.currentDisplay.innerHTML = currentScheduleText;
                        if (schedule.inheritsFromUID !== undefined) {
                            if (schedule.inheritsFromUID.length > 0) {
                                window.htkHelper.getSchedule(
                                    schedule.inheritsFromUID,
                                    function (parentSchedule) {
                                        currentScheduleText += " (" + parentSchedule.name + ")";
                                        this.currentDisplay.innerHTML = currentScheduleText;
                                    }.bind(this),
                                    function (response) {
                                    }
                                );
                            }
                        }
                        window.htkHelper.setCurrentScheduleUID(schedule.uid);
                        window.htkHelper.resetScheduleValuesToCommit();
                        this.setPlantButton.disabled = false;
                    }

                    /**
                     * @brief Callback function that is called when a new reference is selected. Calls setReference.
                     */
                    refererenceScheduleChanged(schedule) {
                        var referenceScheduleText = schedule.name;
                        this.currentReference.innerHTML = referenceScheduleText;
                        if (schedule.inheritsFromUID !== undefined) {
                            if (schedule.inheritsFromUID.length > 0) {
                                window.htkHelper.getSchedule(
                                    schedule.inheritsFromUID,
                                    function (parentSchedule) {
                                        referenceScheduleText += " (" + parentSchedule.name + ")";
                                        this.currentReference.innerHTML = referenceScheduleText;
                                    }.bind(this),
                                    function (response) {
                                    }
                                );
                            }
                        }

                        this.setReference(schedule.uid);
                    }

                    /**
                     * @brief Callback function that is called when the user requests to update the variables values with values from a given schedule. Calls copyFromSchedule.
                     */
                    copyFromScheduleChanged(schedule) {
                        this.copyFromSchedule(schedule.uid, false, true, false, function (){});
                    }

                    /**
                     * @brief Callback function that is called when the user requests to edit a given schedule. Updates the current variables values by calling copyFromSchedule.
                     */
                    editScheduleChanged(schedule) {
                        this.copyFromSchedule(schedule.uid, true, false, false, function() {
                            this.copyFromReferenceScheduleButton.disabled = false;
                            this.copyFromReferencePlantButton.disabled = false;
                            this.commitButton.disabled = false;
                            this.undoButton.disabled = false;
                            this.fireScheduleChanged(schedule);
                        }.bind(this));
                    }

                    /**
                     * @brief Callback function that is called when the user requests to view a given schedule. Updates the current variables values by calling copyFromSchedule.
                     */
                    viewScheduleChanged(schedule) {
                        this.copyFromSchedule(schedule.uid, true, false, true, function() {
                            this.copyFromReferenceScheduleButton.disabled = true;
                            this.copyFromReferencePlantButton.disabled = true;
                            this.commitButton.disabled = true;
                            this.undoButton.disabled = true;
                            this.fireScheduleChanged(schedule);
                        }.bind(this));
                    }

                    /**
                     * @brief Registers a component that wants to be informed about schedule changes.
                     * @param[in] listener the component to register.
                     */
                    addScheduleChangedListener(listener) {
                        this.scheduleChangeListeners.push(listener);
                    }

                    /**
                     * @brief Registers a component that wants to be informed about page changes.
                     * @param[in] listener the component to register.
                     */
                    addPageListener(listener) {
                        this.pageListeners.push(listener);
                    }

                    /**
                     * @brief Registers a component that wants to be informed when the user logsout from the system.
                     * @param[in] listener the component to register.
                     */
                    addUserLogoutListener(listener) {
                        this.userLogoutListeners.push(listener);
                    }

                    /**
                     * @brief Updates the reference on all the hieratika components.
                     * @param[in] currentReference the reference to set as one of:
                     *  - NONE_NAME (resets the reference to NONE)
                     *  - PLANT_NAME (sets the reference as the plant)
                     *  - currentReference a reference with the name currentReference
                     */
                    setReference(currentReference) {
                        HtkDialogs.showWaitDialog();
                        var mainFrameHtkComponents = window.htkHelper.getAllMainFrameHtkComponents();
                        var keys = Object.keys(mainFrameHtkComponents);
                        var htkComp;
                        if (currentReference === Constants.NONE_NAME) {
                            //Reset all the values to N/A
                            for (var i=0; i<keys.length; i++) {
                                var htkCompArray = mainFrameHtkComponents[keys[i]];
                                for (var j=0; j<htkCompArray.length; j++) {
                                    var htkComp = htkCompArray[j];
                                    htkComp.setReferenceValue("N/A");
                                    htkComp.setReference(currentReference);
                                }
                            }
                            HtkDialogs.closeWaitDialog();
                        }
                        else if (currentReference === Constants.PLANT_NAME) {
                            for (var i=0; i<keys.length; i++) {
                                var htkCompArray = mainFrameHtkComponents[keys[i]];
                                for (var j=0; j<htkCompArray.length; j++) {
                                    var htkComp = htkCompArray[j];
                                    htkComp.setReferenceValue(htkComp.getPlantValue());
                                    htkComp.setReference(currentReference);
                                }
                            }
                            HtkDialogs.closeWaitDialog();
                        }
                        else {
                            window.htkHelper.getScheduleVariablesValues(
                                currentReference,
                                function(variables) {
                                    var keys = Object.keys(variables);
                                    for (var i in keys) {
                                        var variableName = keys[i];
                                        var variableValue = variables[keys[i]];
                                        var htkCompArray = mainFrameHtkComponents[variableName];
                                        if (htkCompArray !== undefined) {
                                            for (var j=0; j<htkCompArray.length; j++) {
                                                var htkComp = htkCompArray[j];
                                                htkComp.setReferenceValue(variableValue);
                                                htkComp.setReference(currentReference);
                                            }
                                        }
                                    }
                                    HtkDialogs.closeWaitDialog();
                                },
                                function () {
                                    HtkDialogs.closeWaitDialog();
                                    HtkDialogs.showErrorDialog("Failed to update plant values. Unknown error, check the server logs.");
                                }
                            );
                        }
                    }

                    /**
                     * @brief Copies the values from a given schedule into all the components.
                     * @param[in] schUID the schedule identifier (i.e. the schedule name).
                     * @param[in] resetValue if true, for all the components, the initial value will be set against the retrieved schedule value.
                     * @param[in] updateRemote if true, for all the components, the update will be propagated to the server (see HtkComponent.setValue).
                     * @param[in] setNotEditable if true, for all the components, the component will be set as read-only.
                     * @param[in] successFun the function to be called when all the variables have been copied.
                     */
                    copyFromSchedule(schUID, resetValue, updateRemote, setNotEditable, successFun) {
                        HtkDialogs.showWaitDialog();
                        window.htkHelper.getScheduleVariablesValues(
                            schUID,
                            function (variables) {
                                var keys = Object.keys(variables);
                                var mainFrameHtkComponents = window.htkHelper.getAllMainFrameHtkComponents();
                                for (var i in keys) {
                                    var variableName = keys[i];
                                    var variableValue = variables[keys[i]];
                                    var targetElements = mainFrameHtkComponents[variableName];
                                    if (targetElements != null) {
                                        for (var j=0; j<targetElements.length; j++) {
                                            var targetElement = targetElements[j];
                                            //resetValue = true => change of schedule
                                            var update = resetValue;
                                            if (!update) {
                                                //Do not overwrite locked components!
                                                update = !targetElement.isReadOnly();
                                            }
                                            if (update) {
                                                if (resetValue) {
                                                    targetElement.setInitialValue(variableValue);
                                                }
                                                targetElement.setValue(variableValue, updateRemote);
                                            }
                                            targetElement.setEditable(!setNotEditable);
                                        }
                                    }
                                }
                                successFun();
                            },
                            function () {
                                HtkDialogs.closeWaitDialog();
                                HtkDialogs.showErrorDialog("Failed to copy from the schedule. Unknown error, check the server logs.");
                            }
                        );
                        HtkDialogs.closeWaitDialog();
                    }

                    /**
                     * @brief Undos all the changes that were made to a given schedule.
                     */
                    undoAllChangesToSchedule() {
                        var mainFrameHtkComponents = window.htkHelper.getAllMainFrameHtkComponents();
                        var keys = Object.keys(mainFrameHtkComponents);
                        for (var i=0; i<keys.length; i++) {
                            var htkCompArray = mainFrameHtkComponents[keys[i]];
                            for (var j=0; j<htkCompArray.length; j++) {
                                var htkComp = htkCompArray[j];
                                htkComp.setValue(htkComp.getInitialValue());
                            }
                        }
                    }
                }

                /**
                 * @brief Registers the element.
                 */
                 window.customElements.define('htk-nav', HtkNav);
