/*
 date: 04/01/2018
 author: Andre' Neto

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
        <link rel="import" href="/htk-component.html">
*/

import HtkHelper from './htk-helper.js'
import { HtkDialogs } from './htk-dialogs.js'
import $ from './js/jquery/jquery.js'

const template = document.createElement('template');
template.innerHTML = `
  <iframe id="dmaineditor" style="position: absolute; height: 100%; width: 100%; border: none">
  </iframe>
`;


/**
 * @brief Hieratika main editor. Offers the iframe that contains all the components that represent a given Hieratika page.
 */
export class HtkMainEditor extends HTMLElement {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {
        super();
    }

    /**
     * @brief See HTMLElement.createdCallback.
     */
    connectedCallback () {
      var templateContent = template.content;
      const root = this.attachShadow({mode: 'open'});
      root.appendChild(templateContent.cloneNode(true));
      this.variablesInfoLoadedListeners = [this];
      HtkHelper.setHtkMainEditor(this);
      this.mainEditorIFrame = this.shadowRoot.querySelector("#dmaineditor");
      this.mainEditorIFrame.src = "/help.html?" + new Date().getTime(); //new Date... to force reloading with no caching
    }

    /**
     * @brief See HTMLElement.attachedCallback.
     */
    attachedCallback() {
        var topNav = document.getElementById("nav-pane");
        topNav.addPageListener(this);
        topNav.addUserLogoutListener(this);
        //Cannot be done from the topNav since the topNav createdCallback and attachedCallback are called before the mainEditor created and attached callbacks
        this.addVariablesInfoLoadedListener(topNav);
    }

    /**
     * @brief Registers a component that wants to informed when all the variables information, for a given page, have been loaded.
     * @param[in] listener the component to register.
     */
    addVariablesInfoLoadedListener(listener) {
        this.variablesInfoLoadedListeners.push(listener);
    }

    /**
     * @brief Informs all the registered components (see addVariablesInfoLoadedListener) that a new page has been loaded.
     */
    fireVariablesInfoLoaded() {
        for(var l in this.variablesInfoLoadedListeners) {
            this.variablesInfoLoadedListeners[l].variablesInfoLoaded();
        }
    }

    /**
     * @brief Loads a new page into the main iframe display.
     * @param[in] pageName the page to display.
     */
    loadVariablesInfo(pageName) {
        var htkDialog = new HtkDialogs();
        htkDialog.showWaitDialog();
        var allVariableIds = [];
        var allLiveVariableIds = [];
        var mainFrameComponents = this.mainEditorIFrame.contentDocument._frameComponents;
        for (var k in mainFrameComponents) {
            var comp = mainFrameComponents[k][0];
            if (comp !== undefined) {
                if (comp.isLiveVariable()) {
                    allLiveVariableIds.push(k);
                }
                else {
                    allVariableIds.push(k);
                }
            }
        }
        HtkHelper.getLiveVariablesInfo(
            allLiveVariableIds,
            function (variables) {
                var user = HtkHelper.getUser();
                for (var i in variables) {
                    var variable = variables[i];
                    var targetElements = this.mainEditorIFrame.contentDocument._frameComponents[variable.name];
                    if (targetElements != null) {
                        for (var j in targetElements) {
                            targetElements[j].setVariable(variable);
                        }
                    }
                }
                HtkHelper.getVariablesInfo(
                    pageName,
                    allVariableIds,
                    function (variables) {
                        var user = HtkHelper.getUser();
                        var lockVariableNames = [];
                        for (var i in variables) {
                            var variable = variables[i];
                            var targetElements = this.mainEditorIFrame.contentDocument._frameComponents[variable.name];
                            if (targetElements != null) {
                                for (var j in targetElements) {
                                    targetElements[j].setVariable(variable);
                                    targetElements[j].checkUserAllowedToWrite(user);
                                    if (variable.lockVariable.length > 0) {
                                        targetElements[j].setLockVariable(variable.lockVariable);
                                        var targetLockElements = this.mainEditorIFrame.contentDocument._frameComponents[variable.lockVariable];
                                        if (targetLockElements != null) {
                                            for (var z in targetLockElements) {
                                                targetLockElements[z].addLockStatusChangedListener(targetElements[j]);
                                            }
                                        }
                                    }
                                }
                            }
                            if (variable.lockVariable.length > 0) {
                                lockVariableNames.push(variable.lockVariable);
                            }
                        }

                        this.fireVariablesInfoLoaded();
                        htkDialog.closeWaitDialog();
                    }.bind(this),
                    function () {
                        var htkDialog = new HtkDialogs();
                        htkDialog.showErrorDialog("Failed to get variables info. Unknown error, check the server logs.");
                        htkDialog.closeWaitDialog();
                    }.bind(this)
                );
            }.bind(this),
            function () {
                var htkDialog = new HtkDialogs();
                htkDialog.showErrorDialog("Failed to get live variables info. Unknown error, check the server logs.");
                htkDialog.closeWaitDialog();
            }.bind(this)

        );
    }

    /**
     * @brief Callback function called when the page has finished loading (onload event).
     * @param[in] pageName the page that was loaded.
     */
    iFrameLoaded(pageName) {
        this.loadVariablesInfo(pageName);

        $.each(this.mainEditorIFrame.contentDocument._frameComponents, function (i, htkCompArray) {
            $.each(htkCompArray, function (j, htkComp) {
                htkComp.domLoaded();
            });
        });
    }

    /**
     * @brief Callback function that is called when the page has been changed by the user (see addPageListener on htk-nav-pane).
     * @param[in] page the page that was loaded.
     */
    pageChanged (page) {
        this.mainEditorIFrame.contentDocument._frameComponents = {};
        //Remove all the listeners (apart from this and the htk-nav)
        this.variablesInfoLoadedListeners = this.variablesInfoLoadedListeners.slice(0, 2);
        var pageUrl = "pages/" + page.url + ".html?" + new Date().getTime(); //new Date... to force reloading with no caching
        this.mainEditorIFrame.onload = function(evt) {
            this.iFrameLoaded(page.name);
        }.bind(this);
        this.mainEditorIFrame.src = pageUrl;
    }

    /**
     * @brief Callback function that is called when all the variables information has been loaded.
     */
    variablesInfoLoaded() {
        HtkHelper.displayPlant();
    }

    /**
     * @brief Function called when a user logsout from the system. Displays the help page.
     */
    userLogout () {
        this.mainEditorIFrame.onload = function(evt) {
        }.bind(this);
        this.mainEditorIFrame.src = "/help.html?" + new Date().getTime(); //new Date... to force reloading with no caching

    }

    /**
     * @brief Gets all the components that are registered in the main frame of hieratika.
     * @return The components that are registered in the main frame of hieratika.
     */
    getAllMainFrameHtkComponents() {
        return this.mainEditorIFrame.contentDocument._frameComponents;
    }

    /**
     * @brief Shows the statistics page.
     */
    showStatistics() {
        this.mainEditorIFrame.onload = function(evt) {
        }.bind(this);
        this.mainEditorIFrame.src = "/statistics.html?" + new Date().getTime(); //new Date... to force reloading with no caching
    }

    /**
     * @brief Shows the plant builder page.
     */
    showPlantBuilder() {
        this.mainEditorIFrame.onload = function(evt) {
        }.bind(this);
        this.mainEditorIFrame.src = "/plant-builder.html?" + new Date().getTime(); //new Date... to force reloading with no caching
    }
}


/**
 * @brief Registers the element.
 */
customElements.define('htk-main-editor', HtkMainEditor);
